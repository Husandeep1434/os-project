#include "mongoose.h"
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PROCESSES 100
#define MAX_GANTT 1000

typedef struct {
    char id[16];
    int arrival;
    int burst;
    int priority;
    int rem_burst;
} Process;

typedef struct {
    char id[16];
    int start;
    int end;
} GanttBlock;

typedef struct {
    GanttBlock gantt[MAX_GANTT];
    int gantt_count;
    double energy;
    double tat;
    double wt;
} AlgoResult;

int compare_arrival(const void* a, const void* b) {
    return ((Process*)a)->arrival - ((Process*)b)->arrival;
}

void calc_metrics(Process* orig, int n, AlgoResult* res) {
    double total_tat = 0;
    double total_wt = 0;
    for (int i = 0; i < n; i++) {
        int ct = 0;
        for (int j = res->gantt_count - 1; j >= 0; j--) {
            if (strcmp(res->gantt[j].id, orig[i].id) == 0) {
                ct = res->gantt[j].end;
                break;
            }
        }
        double tat = ct - orig[i].arrival;
        double wt = tat - orig[i].burst;
        total_tat += tat;
        total_wt += wt;
    }
    if (n > 0) {
        res->tat = total_tat / n;
        res->wt = total_wt / n;
    } else {
        res->tat = 0;
        res->wt = 0;
    }
}

void run_fcfs(Process* procs, int n, AlgoResult* res) {
    Process p[MAX_PROCESSES];
    memcpy(p, procs, n * sizeof(Process));
    qsort(p, n, sizeof(Process), compare_arrival);

    int time = 0;
    res->gantt_count = 0;
    res->energy = 0;

    for (int i = 0; i < n; i++) {
        if (time < p[i].arrival) time = p[i].arrival;
        int start = time;
        int end = time + p[i].burst;
        
        strcpy(res->gantt[res->gantt_count].id, p[i].id);
        res->gantt[res->gantt_count].start = start;
        res->gantt[res->gantt_count].end = end;
        res->gantt_count++;
        
        res->energy += (4.0) * (end - start); // 2.0^2
        time = end;
    }
    calc_metrics(procs, n, res);
}

void run_priority(Process* procs, int n, AlgoResult* res) {
    Process p[MAX_PROCESSES];
    memcpy(p, procs, n * sizeof(Process));
    qsort(p, n, sizeof(Process), compare_arrival);

    int time = 0;
    res->gantt_count = 0;
    res->energy = 0;

    int completed = 0;
    int is_completed[MAX_PROCESSES] = {0};

    while (completed < n) {
        int idx = -1;
        int min_prio = 999999;
        
        for (int i = 0; i < n; i++) {
            if (p[i].arrival <= time && !is_completed[i]) {
                if (p[i].priority < min_prio) {
                    min_prio = p[i].priority;
                    idx = i;
                }
            }
        }

        if (idx != -1) {
            int start = time;
            int end = time + p[idx].burst;
            
            strcpy(res->gantt[res->gantt_count].id, p[idx].id);
            res->gantt[res->gantt_count].start = start;
            res->gantt[res->gantt_count].end = end;
            res->gantt_count++;
            
            res->energy += (4.0) * (end - start);
            time = end;
            is_completed[idx] = 1;
            completed++;
        } else {
            time++;
        }
    }
    calc_metrics(procs, n, res);
}

void run_eaas(Process* procs, int n, AlgoResult* res) {
    Process p[MAX_PROCESSES];
    memcpy(p, procs, n * sizeof(Process));
    qsort(p, n, sizeof(Process), compare_arrival);

    int time = 0;
    res->gantt_count = 0;
    res->energy = 0;

    int completed = 0;
    int is_completed[MAX_PROCESSES] = {0};

    while (completed < n) {
        int idx = -1;
        int min_prio = 999999;
        int min_burst = 999999;
        
        for (int i = 0; i < n; i++) {
            if (p[i].arrival <= time && !is_completed[i]) {
                if (p[i].priority < min_prio) {
                    min_prio = p[i].priority;
                    min_burst = p[i].burst;
                    idx = i;
                } else if (p[i].priority == min_prio && p[i].burst < min_burst) {
                    min_burst = p[i].burst;
                    idx = i;
                }
            }
        }

        if (idx != -1) {
            int start = time;
            int end = time + p[idx].burst;
            
            strcpy(res->gantt[res->gantt_count].id, p[idx].id);
            res->gantt[res->gantt_count].start = start;
            res->gantt[res->gantt_count].end = end;
            res->gantt_count++;
            
            double burst_dur = end - start;
            double freq = 2.0;
            if (burst_dur <= 3) freq = 1.0;
            else if (burst_dur <= 6) freq = 1.5;
            
            res->energy += (freq * freq) * burst_dur;
            
            time = end;
            is_completed[idx] = 1;
            completed++;
        } else {
            time++;
        }
    }
    calc_metrics(procs, n, res);
}

void run_rr(Process* procs, int n, int tq, AlgoResult* res) {
    Process p[MAX_PROCESSES];
    memcpy(p, procs, n * sizeof(Process));
    qsort(p, n, sizeof(Process), compare_arrival);
    for(int i=0; i<n; i++) p[i].rem_burst = p[i].burst;

    int time = 0;
    res->gantt_count = 0;
    res->energy = 0;

    int queue[MAX_PROCESSES];
    int front = 0, rear = 0;
    int in_queue[MAX_PROCESSES] = {0};
    int completed = 0;
    
    if (n > 0) {
        time = p[0].arrival;
        queue[rear++] = 0;
        in_queue[0] = 1;
    }

    while (completed < n) {
        if (front == rear) {
            int next_arr = 999999;
            for(int i=0; i<n; i++) {
                if (p[i].rem_burst > 0 && p[i].arrival < next_arr) {
                    next_arr = p[i].arrival;
                }
            }
            time = next_arr;
            for(int i=0; i<n; i++) {
                if (p[i].rem_burst > 0 && p[i].arrival <= time && !in_queue[i]) {
                    queue[rear++] = i;
                    in_queue[i] = 1;
                }
            }
        }
        
        int idx = queue[front++];
        int start = time;
        int exec_time = p[idx].rem_burst < tq ? p[idx].rem_burst : tq;
        time += exec_time;
        p[idx].rem_burst -= exec_time;
        
        strcpy(res->gantt[res->gantt_count].id, p[idx].id);
        res->gantt[res->gantt_count].start = start;
        res->gantt[res->gantt_count].end = time;
        res->gantt_count++;
        
        res->energy += (4.0) * exec_time;
        
        for (int i = 0; i < n; i++) {
            if (p[i].rem_burst > 0 && p[i].arrival > start && p[i].arrival <= time && !in_queue[i]) {
                queue[rear++] = i;
                in_queue[i] = 1;
            }
        }
        
        if (p[idx].rem_burst > 0) {
            queue[rear++] = idx;
        } else {
            completed++;
        }
    }
    calc_metrics(procs, n, res);
}

cJSON* result_to_json(AlgoResult* res) {
    cJSON* obj = cJSON_CreateObject();
    cJSON_AddNumberToObject(obj, "energy", res->energy);
    cJSON_AddNumberToObject(obj, "tat", res->tat);
    cJSON_AddNumberToObject(obj, "wt", res->wt);
    
    cJSON* gantt = cJSON_CreateArray();
    for (int i = 0; i < res->gantt_count; i++) {
        cJSON* block = cJSON_CreateArray();
        cJSON_AddItemToArray(block, cJSON_CreateString(res->gantt[i].id));
        cJSON_AddItemToArray(block, cJSON_CreateNumber(res->gantt[i].start));
        cJSON_AddItemToArray(block, cJSON_CreateNumber(res->gantt[i].end));
        cJSON_AddItemToArray(gantt, block);
    }
    cJSON_AddItemToObject(obj, "gantt", gantt);
    return obj;
}

static void ev_handler(struct mg_connection *c, int ev, void *ev_data) {
    if (ev == MG_EV_HTTP_MSG) {
        struct mg_http_message *hm = (struct mg_http_message *) ev_data;

        if (mg_match(hm->uri, mg_str("/simulate"), NULL)) {
            char* body = (char*)malloc(hm->body.len + 1);
            memcpy(body, hm->body.buf, hm->body.len);
            body[hm->body.len] = '\0';
            
            cJSON *json = cJSON_Parse(body);
            free(body);

            if (json == NULL) {
                mg_http_reply(c, 400, "", "{\"error\": \"Invalid JSON\"}");
                return;
            }

            cJSON *procs_array = cJSON_GetObjectItem(json, "processes");
            cJSON *tq_item = cJSON_GetObjectItem(json, "time_quantum");
            int tq = tq_item ? tq_item->valueint : 2;

            Process procs[MAX_PROCESSES];
            int n = 0;

            if (procs_array != NULL && cJSON_IsArray(procs_array)) {
                cJSON *p_item = NULL;
                cJSON_ArrayForEach(p_item, procs_array) {
                    if (n >= MAX_PROCESSES) break;
                    cJSON *id = cJSON_GetObjectItem(p_item, "id");
                    cJSON *arrival = cJSON_GetObjectItem(p_item, "arrival");
                    cJSON *burst = cJSON_GetObjectItem(p_item, "burst");
                    cJSON *priority = cJSON_GetObjectItem(p_item, "priority");

                    if (id) strcpy(procs[n].id, id->valuestring);
                    if (arrival) procs[n].arrival = atoi(arrival->valuestring);
                    if (burst) procs[n].burst = atoi(burst->valuestring);
                    if (priority) procs[n].priority = atoi(priority->valuestring);
                    n++;
                }
            }

            AlgoResult res_fcfs, res_priority, res_eaas, res_rr;
            run_fcfs(procs, n, &res_fcfs);
            run_priority(procs, n, &res_priority);
            run_eaas(procs, n, &res_eaas);
            run_rr(procs, n, tq, &res_rr);

            cJSON* resp = cJSON_CreateObject();
            cJSON_AddItemToObject(resp, "fcfs", result_to_json(&res_fcfs));
            cJSON_AddItemToObject(resp, "priority", result_to_json(&res_priority));
            cJSON_AddItemToObject(resp, "eaas", result_to_json(&res_eaas));
            cJSON_AddItemToObject(resp, "rr", result_to_json(&res_rr));

            char *json_str = cJSON_PrintUnformatted(resp);
            mg_http_reply(c, 200, "Content-Type: application/json\r\n", "%s", json_str);

            free(json_str);
            cJSON_Delete(resp);
            cJSON_Delete(json);

        } else if (mg_match(hm->uri, mg_str("/"), NULL) || mg_match(hm->uri, mg_str("/index.html"), NULL)) {
            struct mg_http_serve_opts opts = {.root_dir = "."};
            mg_http_serve_file(c, hm, "index.html", &opts);
        } else {
            struct mg_http_serve_opts opts = {.root_dir = "."};
            mg_http_serve_dir(c, hm, &opts);
        }
    }
}

int main(void) {
    struct mg_mgr mgr;
    mg_mgr_init(&mgr);
    mg_http_listen(&mgr, "http://0.0.0.0:9000", ev_handler, NULL);
    printf("Starting server on port 8000...\n");
    for (;;) {
        mg_mgr_poll(&mgr, 1000);
    }
    mg_mgr_free(&mgr);
    return 0;
}
