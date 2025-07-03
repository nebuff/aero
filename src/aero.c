#include <ncurses.h>
#include <stdlib.h>
#include <string.h>



#define MAX_APPS 16
#define APP_NAME_LEN 64
#define APP_ALIAS_LEN 128


#define SETTINGS_KEY_LEN 16
#define COLOR_NAME_LEN 16

// Settings struct for special key config and color config
typedef struct {
    char nav_mode[SETTINGS_KEY_LEN]; // "letters" or "function_keys"
    char app_fg[COLOR_NAME_LEN];     // e.g. "cyan"
    char app_bg[COLOR_NAME_LEN];     // e.g. "black"
    char sel_fg[COLOR_NAME_LEN];     // e.g. "black"
    char sel_bg[COLOR_NAME_LEN];     // e.g. "yellow"
} AeroSettings;

AeroSettings aero_settings = { .nav_mode = "letters", .app_fg = "cyan", .app_bg = "black", .sel_fg = "black", .sel_bg = "yellow" };

#include <stdio.h>
#include <stdbool.h>


typedef struct {
    char name[APP_NAME_LEN];
    char alias[APP_ALIAS_LEN];
    int entertoreturn; // 0 = auto return, 1 = wait for enter
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
    // Look for settings object (e.g. {"settings": {"nav_mode": "letters", ...}})
    char *settings_p = strstr(buf, "\"settings\"");
    if (settings_p) {
        // nav_mode
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
        // app_fg
        char *fg_p = strstr(settings_p, "\"app_fg\"");
        if (fg_p) {
            fg_p = strchr(fg_p, ':');
            if (fg_p) {
                fg_p++;
                while (*fg_p == ' ' || *fg_p == '"') fg_p++;
                char *fg_e = strchr(fg_p, '"');
                if (fg_e) {
                    int fg_len = fg_e - fg_p;
                    if (fg_len > 0 && fg_len < COLOR_NAME_LEN) {
                        strncpy(aero_settings.app_fg, fg_p, fg_len);
                        aero_settings.app_fg[fg_len] = 0;
                    }
                }
            }
        }
        // app_bg
        char *bg_p = strstr(settings_p, "\"app_bg\"");
        if (bg_p) {
            bg_p = strchr(bg_p, ':');
            if (bg_p) {
                bg_p++;
                while (*bg_p == ' ' || *bg_p == '"') bg_p++;
                char *bg_e = strchr(bg_p, '"');
                if (bg_e) {
                    int bg_len = bg_e - bg_p;
                    if (bg_len > 0 && bg_len < COLOR_NAME_LEN) {
                        strncpy(aero_settings.app_bg, bg_p, bg_len);
                        aero_settings.app_bg[bg_len] = 0;
                    }
                }
            }
        }
        // sel_fg
        char *sf_p = strstr(settings_p, "\"sel_fg\"");
        if (sf_p) {
            sf_p = strchr(sf_p, ':');
            if (sf_p) {
                sf_p++;
                while (*sf_p == ' ' || *sf_p == '"') sf_p++;
                char *sf_e = strchr(sf_p, '"');
                if (sf_e) {
                    int sf_len = sf_e - sf_p;
                    if (sf_len > 0 && sf_len < COLOR_NAME_LEN) {
                        strncpy(aero_settings.sel_fg, sf_p, sf_len);
                        aero_settings.sel_fg[sf_len] = 0;
                    }
                }
            }
        }
        // sel_bg
        char *sb_p = strstr(settings_p, "\"sel_bg\"");
        if (sb_p) {
            sb_p = strchr(sb_p, ':');
            if (sb_p) {
                sb_p++;
                while (*sb_p == ' ' || *sb_p == '"') sb_p++;
                char *sb_e = strchr(sb_p, '"');
                if (sb_e) {
                    int sb_len = sb_e - sb_p;
                    if (sb_len > 0 && sb_len < COLOR_NAME_LEN) {
                        strncpy(aero_settings.sel_bg, sb_p, sb_len);
                        aero_settings.sel_bg[sb_len] = 0;
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
        // Look for entertoreturn (default: 0)
        apps[app_count].entertoreturn = 0;
        char *e = strstr(ae, "\"entertoreturn\"");
        if (e) {
            e = strchr(e, ':');
            if (e) {
                e++;
                while (*e == ' ' || *e == '"') e++;
                if (strncmp(e, "true", 4) == 0 || *e == '1') {
                    apps[app_count].entertoreturn = 1;
                }
            }
        }
        app_count++;
        p = ae;
    }
    return app_count > 0;
}

// Color name to ncurses color
int color_from_name(const char *name) {
    if (strcasecmp(name, "black") == 0) return COLOR_BLACK;
    if (strcasecmp(name, "red") == 0) return COLOR_RED;
    if (strcasecmp(name, "green") == 0) return COLOR_GREEN;
    if (strcasecmp(name, "yellow") == 0) return COLOR_YELLOW;
    if (strcasecmp(name, "blue") == 0) return COLOR_BLUE;
    if (strcasecmp(name, "magenta") == 0) return COLOR_MAGENTA;
    if (strcasecmp(name, "cyan") == 0) return COLOR_CYAN;
    if (strcasecmp(name, "white") == 0) return COLOR_WHITE;
    return COLOR_WHITE;
}

void draw_menu(int highlight, bool in_settings) {
    clear();
    if (in_settings) {
        mvprintw(0, 2, "Aero Settings");
        mvprintw(1, 2, "Use arrow keys, Enter to select, q to return.");
        for (int i = 0; i < 4; ++i) {
            if (i == highlight) {
                attron(COLOR_PAIR(2));
            } else {
                attron(COLOR_PAIR(1));
            }
            switch (i) {
                case 0: mvprintw(3, 4, "Update Aero"); break;
                case 1: mvprintw(4, 4, "Edit App List"); break;
                case 2: mvprintw(5, 4, "Back"); break;
                case 3: mvprintw(7, 4, "Special Key Mode: %s", strcmp(aero_settings.nav_mode, "function_keys") == 0 ? "Function Keys" : "Letters"); break;
            }
            if (i == highlight) {
                attroff(COLOR_PAIR(2));
            } else {
                attroff(COLOR_PAIR(1));
            }
        }
        mvprintw(8, 4, "(Toggle and save to app-list.txt)");
        mvprintw(10, 2, "App Color: fg=%s bg=%s", aero_settings.app_fg, aero_settings.app_bg);
        mvprintw(11, 2, "Selected Color: fg=%s bg=%s", aero_settings.sel_fg, aero_settings.sel_bg);
        mvprintw(12, 2, "Edit app-list.txt to change colors.");
    } else {
        mvprintw(0, 2, "Aero App Center (TUI)");
        if (strcmp(aero_settings.nav_mode, "function_keys") == 0) {
            mvprintw(1, 2, "F1: Quit, F2: Settings, arrows to navigate, Enter to select");
        } else {
            mvprintw(1, 2, "Use arrow keys, Enter to select, q to quit, s for settings.");
        }
        for (int i = 0; i < app_count; ++i) {
            if (i == highlight) {
                attron(COLOR_PAIR(2));
                mvprintw(i + 3, 4, "%s", apps[i].name);
                attroff(COLOR_PAIR(2));
            } else {
                attron(COLOR_PAIR(1));
                mvprintw(i + 3, 4, "%s", apps[i].name);
                attroff(COLOR_PAIR(1));
            }
        }
    }
    refresh();
}


// Save nav_mode and color settings to app-list.txt (preserves apps, rewrites settings)
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
    fprintf(out,
        "{\"settings\":{\"nav_mode\":\"%s\",\"app_fg\":\"%s\",\"app_bg\":\"%s\",\"sel_fg\":\"%s\",\"sel_bg\":\"%s\"}},\n",
        aero_settings.nav_mode,
        aero_settings.app_fg,
        aero_settings.app_bg,
        aero_settings.sel_fg,
        aero_settings.sel_bg);
    fputs(apps_start, out);
    fclose(out);
}


int main() {
    // Only use /aero/app-list.txt for all Aero data/configs
    const char *applist_paths[] = {"/aero/app-list.txt"};
    int applist_idx = -1;
    for (int i = 0; i < 1; ++i) {
        if (load_apps(applist_paths[i])) {
            applist_idx = i;
            break;
        }
    }
    if (applist_idx == -1) {
        printf("No /aero/app-list.txt found!\n\n");
        printf("Please run the installer script to set up Aero:\n");
        printf("To add apps, edit /aero/app-list.txt and add entries like:\n");
        printf("  [\n    {\"name\": \"Text Editor\", \"alias\": \"nano\" }\n  ]\n");
        printf("You can use any text editor, e.g. 'nano /aero/app-list.txt'\n");
        return 1;
    }
    initscr();
    if (has_colors()) {
        start_color();
        // Color pairs: 1 = app, 2 = selected, 3 = settings highlight
        init_pair(1, color_from_name(aero_settings.app_fg), color_from_name(aero_settings.app_bg));
        init_pair(2, color_from_name(aero_settings.sel_fg), color_from_name(aero_settings.sel_bg));
        init_pair(3, color_from_name(aero_settings.sel_fg), color_from_name(aero_settings.sel_bg));
    }
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
                        system("nano /aero/app-list.txt");
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
                // Clear the terminal before running the application
                system("clear");
                // Removed launch message
                char cmd[APP_ALIAS_LEN + 32];
                snprintf(cmd, sizeof(cmd), "%s", apps[highlight].alias);
                system(cmd);
                if (apps[highlight].entertoreturn) {
                    printf("\nPress Enter to return to Aero...");
                    getchar();
                }
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
