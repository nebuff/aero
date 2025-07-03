#include <ncurses.h>
#include <stdlib.h>
#include <string.h>


#define MAX_APPS 16
#define APP_NAME_LEN 64
#define APP_ALIAS_LEN 128

#include <stdio.h>
#include <stdbool.h>

typedef struct {
    char name[APP_NAME_LEN];
    char alias[APP_ALIAS_LEN];
} App;

App apps[MAX_APPS];
int app_count = 0;

// Simple JSON parser for the app-list.txt format
bool load_apps(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) return false;
    char buf[4096];
    size_t len = fread(buf, 1, sizeof(buf)-1, f);
    buf[len] = 0;
    fclose(f);
    char *p = buf;
    app_count = 0;
    while ((p = strstr(p, "{\"name\"")) && app_count < MAX_APPS) {
        char *n = strstr(p, ":");
        if (!n) break;
        n++;
        while (*n == ' ' || *n == '"') n++;
        char *ne = strchr(n, '"');
        if (!ne) break;
        int nlen = ne-n;
        strncpy(apps[app_count].name, n, nlen);
        apps[app_count].name[nlen] = 0;
        char *a = strstr(ne, "\"alias\"");
        if (!a) break;
        a = strchr(a, ':');
        if (!a) break;
        a++;
        while (*a == ' ' || *a == '"') a++;
        char *ae = strchr(a, '"');
        if (!ae) break;
        int alen = ae-a;
        strncpy(apps[app_count].alias, a, alen);
        apps[app_count].alias[alen] = 0;
        app_count++;
        p = ae;
    }
    return app_count > 0;
}

void draw_menu(int highlight, bool in_settings) {
    clear();
    if (in_settings) {
        mvprintw(0, 2, "Aero Settings");
        mvprintw(1, 2, "Use arrow keys, Enter to select, q to return.");
        if (highlight == 0) attron(A_REVERSE);
        mvprintw(3, 4, "Update Aero");
        if (highlight == 0) attroff(A_REVERSE);
        if (highlight == 1) attron(A_REVERSE);
        mvprintw(4, 4, "Edit App List");
        if (highlight == 1) attroff(A_REVERSE);
        if (highlight == 2) attron(A_REVERSE);
        mvprintw(5, 4, "Back");
        if (highlight == 2) attroff(A_REVERSE);
    } else {
        mvprintw(0, 2, "Aero App Center (TUI)");
        mvprintw(1, 2, "Use arrow keys to navigate, Enter to select, q to quit, s for settings.");
        for (int i = 0; i < app_count; ++i) {
            if (i == highlight)
                attron(A_REVERSE);
            mvprintw(i + 3, 4, "%s", apps[i].name);
            if (i == highlight)
                attroff(A_REVERSE);
        }
    }
    refresh();
}

int main() {
    if (!load_apps("../app-list.txt") &&
        !load_apps("app-list.txt") &&
        !load_apps("/usr/local/share/aero/app-list.txt")) {
        printf("No app-list.txt found!\n\n");
        printf("To add apps, edit /usr/local/share/aero/app-list.txt and add entries like:\n");
        printf("  [\n    {\"name\": \"Text Editor\", \"alias\": \"nano\" }\n  ]\n");
        printf("You can use any text editor, e.g. 'sudo nano /usr/local/share/aero/app-list.txt'\n");
        return 1;
    }
    initscr();
    clear();
    noecho();
    cbreak();
    keypad(stdscr, TRUE);

    int highlight = 0;
    int ch;
    bool in_settings = false;
    int settings_highlight = 0;
    draw_menu(highlight, in_settings);
    while (1) {
        ch = getch();
        if (!in_settings && ch == 'q') break;
        if (!in_settings && ch == 's') {
            in_settings = true;
            settings_highlight = 0;
            draw_menu(settings_highlight, in_settings);
            continue;
        }
        if (in_settings && ch == 'q') {
            in_settings = false;
            draw_menu(highlight, in_settings);
            continue;
        }
        if (in_settings) {
            switch (ch) {
                case KEY_UP:
                    if (settings_highlight > 0) --settings_highlight;
                    break;
                case KEY_DOWN:
                    if (settings_highlight < 2) ++settings_highlight;
                    break;
                case '\n':
                    if (settings_highlight == 0) {
                        endwin();
                        printf("Updating Aero...\n");
                        system("curl -fsSL https://raw.githubusercontent.com/nebuff/aero/refs/heads/main/update.sh | sh");
                        printf("Press Enter to continue...");
                        getchar();
                        initscr();
                    } else if (settings_highlight == 1) {
                        endwin();
                        printf("Opening app-list.txt in nano...\n");
                        system("sudo nano /usr/local/share/aero/app-list.txt");
                        printf("Press Enter to continue...");
                        getchar();
                        initscr();
                    }
                    in_settings = false;
                    break;
            }
            draw_menu(settings_highlight, in_settings);
            continue;
        }
        switch (ch) {
            case KEY_UP:
                if (highlight > 0) --highlight;
                break;
            case KEY_DOWN:
                if (highlight < app_count - 1) ++highlight;
                break;
            case '\n':
                endwin();
                printf("Launching: %s\n", apps[highlight].alias);
                char cmd[APP_ALIAS_LEN + 32];
                snprintf(cmd, sizeof(cmd), "%s", apps[highlight].alias);
                system(cmd);
                printf("\nPress Enter to return to Aero...");
                getchar();
                initscr();
                clear();
                noecho();
                cbreak();
                keypad(stdscr, TRUE);
                break;
        }
        draw_menu(highlight, in_settings);
    }
    endwin();
    return 0;
}
