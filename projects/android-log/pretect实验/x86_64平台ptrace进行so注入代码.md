### inject.c


```
#include<sys/ptrace.h>
#include<sys/reg.h>
#include<sys/wait.h>
#include<sys/user.h>
#include<stdlib.h>
#include<errno.h>
#include<string.h>
#include<stdio.h>

//如果命令参数不包含进程名，则直接跟踪surfaceflinger进程
int main(int argc, char** argv) {
	int i =0;
	char *pid_name = NULL;
	if (argc > 1){
		for(i=1; i < argc; i++){
			pid_name = argv[i];
			inject(pid_name);
		}
	}
	else {
		pid_name = "/system/bin/surfaceflinger";
		inject(pid_name);
	}
	return 0;
}

//注入以pid_name为名的进程中
int inject(char* pid_name){
	int* target_pid = find_pid_of(pid_name);
	if (-1 == target_pid) {
		printf("Can't find the process: %s\n", pid_name);
		return -1;
	}

    int i;
    for(i=0;i<10;i++){
        if(target_pid[i] > 0) {
            printf("Try to inject the process: %d\n", target_pid[i]);
            inject_remote_process(target_pid[i], "/data/local/tmp/libhookbinder.so", "hook_entry",
                                  pid_name, strlen(pid_name));
        }
    }
    free(target_pid);
	return 0;
}

int* find_pid_of(const char *process_name)
{
	int id;
	DIR* dir;
	FILE *fp;
	char filename[32];
	char cmdline[256];
	struct dirent * entry;

	pid_t* pids = (pid_t*)malloc(sizeof(pid_t)*10);
	int i;
	for(i=0;i<10;i++) pids[i] = -1;
    i = 0;


	if (process_name == NULL)
		return -1;

	dir = opendir("/proc");
	if (dir == NULL)
		return -1;

	while((entry = readdir(dir)) != NULL) {
		id = atoi(entry->d_name);
		if (id != 0) {
			sprintf(filename, "/proc/%d/cmdline", id);
			fp = fopen(filename, "r");
			if (fp) {
				fgets(cmdline, sizeof(cmdline), fp);
				fclose(fp);

				if (strcmp(process_name, cmdline) == 0) {
					/* process found */
					pids[i++] = id;
				}
			}
		}
	}

	closedir(dir);
	return pids;
}
```
