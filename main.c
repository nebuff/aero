
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main() {
    const char *AERO_VERSION = "0.1.0";
    printf("Welcome to Aero Shell! (v%s)\n", AERO_VERSION);
    printf("Type 'help' to see available commands. Type 'exit' to quit.\n");
    char input[256];
    char cwd[1024];
    char components_path[512] = "";
    // Try $HOME/aero/components first, then ./components
    const char *home = getenv("HOME");
    if (home) {
        snprintf(components_path, sizeof(components_path), "%s/aero/components", home);
    } else {
        strcpy(components_path, "./components");
    }
    // Load custom prompt if set
    char prompt[256] = "";
    char *prompt_ptr = NULL;
    FILE *pf = fopen("$HOME/.config/aero/prompt.conf", "r");
    if (!pf) pf = fopen("/Users/holden/.config/aero/prompt.conf", "r"); // fallback for dev
    if (pf) {
        if (fgets(prompt, sizeof(prompt), pf)) {
            char *nl = strchr(prompt, '\n');
            if (nl) *nl = 0;
            prompt_ptr = prompt;
        }
        fclose(pf);
    }
    while (1) {
        if (prompt_ptr && strlen(prompt_ptr) > 0) {
            printf("%s", prompt_ptr);
        } else if (getcwd(cwd, sizeof(cwd)) != NULL) {
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
            char cmd[600];
            snprintf(cmd, sizeof(cmd), "ls '%s'", components_path);
            int ret = system(cmd);
            if (ret != 0) printf("No components directory found at %s\n", components_path);
            continue;
        }
        if (strcmp(input, "update") == 0) {
            printf("Updating Aero...\n");
            char update_cmd[1024];
            snprintf(update_cmd, sizeof(update_cmd), "curl -fsSL https://raw.githubusercontent.com/nebuff/aero/main/install.sh | sh");
            int ret = system(update_cmd);
            if (ret == 0) {
                printf("Aero updated! Please restart your shell.\n");
            } else {
                printf("Aero update failed.\n");
            }
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
