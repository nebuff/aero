
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main() {
    printf("Welcome to Aero Shell!\n");
    printf("Type 'help' to see available commands. Type 'exit' to quit.\n");
    char input[256];
    char cwd[1024];
    while (1) {
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            printf("aero:%s$ ", cwd);
        } else {
            printf("aero$ ");
        }
        if (!fgets(input, sizeof(input), stdin)) break;
        // Remove newline
        char *newline = strchr(input, '\n');
        if (newline) *newline = 0;
        if (strcmp(input, "exit") == 0) break;
        if (strcmp(input, "help") == 0) {
            printf("Built-in commands:\n");
            printf("  cd <dir>      - Change directory\n");
            printf("  ls [dir]      - List directory contents\n");
            printf("  mkdir <dir>   - Create directory\n");
            printf("  rmdir <dir>   - Remove directory\n");
            printf("  rm <file>     - Remove file\n");
            printf("  touch <file>  - Create empty file\n");
            printf("  cat <file>    - Show file contents\n");
            printf("  pwd           - Print working directory\n");
            printf("  echo <text>   - Print text\n");
            printf("  clear         - Clear the screen\n");
            printf("  list          - List Aero components\n");
            printf("  run <comp>    - Run Aero component\n");
            printf("  help          - Show this help\n");
            printf("  exit          - Exit Aero\n");
            continue;
        }
        if (strncmp(input, "cd ", 3) == 0) {
            char *dir = input + 3;
            if (chdir(dir) != 0) perror("cd");
            continue;
        }
        if (strcmp(input, "pwd") == 0) {
            if (getcwd(cwd, sizeof(cwd)) != NULL) printf("%s\n", cwd);
            continue;
        }
        if (strncmp(input, "ls", 2) == 0) {
            char cmd[512] = "ls ";
            if (strlen(input) > 2) strncat(cmd, input+2, sizeof(cmd)-strlen(cmd)-1);
            system(cmd);
            continue;
        }
        if (strncmp(input, "mkdir ", 6) == 0) {
            char cmd[512];
            snprintf(cmd, sizeof(cmd), "mkdir '%s'", input+6);
            system(cmd);
            continue;
        }
        if (strncmp(input, "rmdir ", 6) == 0) {
            char cmd[512];
            snprintf(cmd, sizeof(cmd), "rmdir '%s'", input+6);
            system(cmd);
            continue;
        }
        if (strncmp(input, "rm ", 3) == 0) {
            char cmd[512];
            snprintf(cmd, sizeof(cmd), "rm '%s'", input+3);
            system(cmd);
            continue;
        }
        if (strncmp(input, "touch ", 6) == 0) {
            char cmd[512];
            snprintf(cmd, sizeof(cmd), "touch '%s'", input+6);
            system(cmd);
            continue;
        }
        if (strncmp(input, "cat ", 4) == 0) {
            char cmd[512];
            snprintf(cmd, sizeof(cmd), "cat '%s'", input+4);
            system(cmd);
            continue;
        }
        if (strncmp(input, "echo ", 5) == 0) {
            printf("%s\n", input+5);
            continue;
        }
        if (strcmp(input, "clear") == 0) {
            system("clear");
            continue;
        }
        if (strcmp(input, "list") == 0) {
            system("ls ../components");
            continue;
        }
        if (strncmp(input, "run ", 4) == 0) {
            char cmd[512];
            snprintf(cmd, sizeof(cmd), "sh ../components/%s", input+4);
            system(cmd);
            continue;
        }
        // Fallback: try to run as a system command
        int ret = system(input);
        if (ret == -1) printf("Unknown command: %s\n", input);
    }
    return 0;
}
