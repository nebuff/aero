#include <ncurses.h>
#include <stdlib.h>
#include <string.h>



#define MAX_APPS 16
#define APP_NAME_LEN 64
#define APP_ALIAS_LEN 128

#define SETTINGS_KEY_LEN 16

// Settings struct for special key config
typedef struct {
    char nav_mode[SETTINGS_KEY_LEN]; // "letters" or "function_keys"
} AeroSettings;

AeroSettings aero_settings = { .nav_mode = "letters" };

#include <stdio.h>
#include <stdbool.h>

typedef struct {
    char name[APP_NAME_LEN];
    char alias[APP_ALIAS_LEN];
} App;

App apps[MAX_APPS];
int app_count = 0;


// Simple JSON parser for the app-list.txt format, also loads settings if present
bool load_apps(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) return false;
    char buf[4096];
    size_t len = fread(buf, 1, sizeof(buf)-1, f);
    buf[len] = 0;
    fclose(f);
    char *p = buf;
    app_count = 0;
    // Look for settings object (e.g. {"settings": {"nav_mode": "letters"}})
    char *settings_p = strstr(buf, "\"settings\"");
    if (settings_p) {
        char *nav_p = strstr(settings_p, "\"nav_mode\"");
        if (nav_p) {
            nav_p = strchr(nav_p, ':');
            if (nav_p) {
                nav_p++;
                while (*nav_p == ' ' || *nav_p == '"') nav_p++;
                char *nav_e = strchr(nav_p, '"');
                if (nav_e) {
                    int nav_len = nav_e - nav_p;
                    if (nav_len > 0 && nav_len < SETTINGS_KEY_LEN) {
                        strncpy(aero_settings.nav_mode, nav_p, nav_len);
                        aero_settings.nav_mode[nav_len] = 0;
                    }
                }
            }
        }
    }
    // Parse apps as before
    p = buf;
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
        if (highlight == 3) attron(A_REVERSE);
        mvprintw(7, 4, "Special Key Mode: %s", strcmp(aero_settings.nav_mode, "function_keys") == 0 ? "Function Keys" : "Letters");
        if (highlight == 3) attroff(A_REVERSE);
        mvprintw(8, 4, "(Toggle and save to app-list.txt)");
    } else {
        mvprintw(0, 2, "Aero App Center (TUI)");
        if (strcmp(aero_settings.nav_mode, "function_keys") == 0) {
            mvprintw(1, 2, "F1: Quit, F2: Settings, arrows to navigate, Enter to select");
        } else {
            mvprintw(1, 2, "Use arrow keys, Enter to select, q to quit, s for settings.");
        }
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


// Save nav_mode setting to app-list.txt (preserves apps, rewrites settings)
void save_settings(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) return;
    char buf[4096];
    size_t len = fread(buf, 1, sizeof(buf)-1, f);
    buf[len] = 0;
    fclose(f);
    // Remove any old settings object
    char *apps_start = strchr(buf, '[');
    if (!apps_start) return;
    FILE *out = fopen(filename, "w");
    if (!out) return;
    fprintf(out, "{\"settings\":{\"nav_mode\":\"%s\"}},\n", aero_settings.nav_mode);
    fputs(apps_start, out);
    fclose(out);
}

int main() {
    const char *applist_paths[] = {"../app-list.txt", "app-list.txt", "/usr/local/share/aero/app-list.txt"};
    int applist_idx = -1;
    for (int i = 0; i < 3; ++i) {
        if (load_apps(applist_paths[i])) {
            applist_idx = i;
            break;
        }
    }
    if (applist_idx == -1) {
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
    int settings_max = 4; // 0:Update, 1:Edit, 2:Back, 3:Special Key Mode
    draw_menu(highlight, in_settings);
    while (1) {
        ch = getch();
        if (!in_settings) {
            if ((strcmp(aero_settings.nav_mode, "function_keys") == 0 && ch == KEY_F(1)) || (strcmp(aero_settings.nav_mode, "letters") == 0 && ch == 'q')) break;
            if ((strcmp(aero_settings.nav_mode, "function_keys") == 0 && ch == KEY_F(2)) || (strcmp(aero_settings.nav_mode, "letters") == 0 && ch == 's')) {
                in_settings = true;
                settings_highlight = 0;
                draw_menu(settings_highlight, in_settings);
                continue;
            }
        } else {
            if ((strcmp(aero_settings.nav_mode, "function_keys") == 0 && ch == KEY_F(1)) || (strcmp(aero_settings.nav_mode, "letters") == 0 && ch == 'q')) {
                in_settings = false;
                draw_menu(highlight, in_settings);
                continue;
            }
        }
        if (in_settings) {
            switch (ch) {
                case KEY_UP:
                    if (settings_highlight > 0) --settings_highlight;
                    break;
                case KEY_DOWN:
                    if (settings_highlight < settings_max - 1) ++settings_highlight;
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
                    } else if (settings_highlight == 3) {
                        // Toggle nav_mode
                        if (strcmp(aero_settings.nav_mode, "function_keys") == 0) {
                            strcpy(aero_settings.nav_mode, "letters");
                        } else {
                            strcpy(aero_settings.nav_mode, "function_keys");
                        }
                        // Save to app-list.txt
                        save_settings(applist_paths[applist_idx]);
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
