#include <unistd.h>
#include <dirent.h>

// Battery monitor for Linux/macOS (robust for BAT0/BAT1/etc)
int get_battery_percent() {
#ifdef __APPLE__
    FILE *fp = popen("pmset -g batt | grep -o '[0-9]*%' | head -n1 | tr -d '%'", "r");
    if (!fp) return -1;
    char buf[8];
    if (!fgets(buf, sizeof(buf), fp)) {
        pclose(fp);
        return -1;
    }
    pclose(fp);
    int percent = atoi(buf);
    if (percent < 0 || percent > 100) return -1;
    return percent;
#else
    // Look for any BAT* directory
    DIR *d = opendir("/sys/class/power_supply");
    if (!d) return -1;
    struct dirent *ent;
    char batpath[256];
    int found = 0;
    while ((ent = readdir(d))) {
        if (strncmp(ent->d_name, "BAT", 3) == 0) {
            snprintf(batpath, sizeof(batpath), "/sys/class/power_supply/%s/capacity", ent->d_name);
            found = 1;
            break;
        }
    }
    closedir(d);
    if (!found) return -1;
    FILE *f = fopen(batpath, "r");
    if (!f) return -1;
    int percent = -1;
    if (fscanf(f, "%d", &percent) != 1) percent = -1;
    fclose(f);
    if (percent < 0 || percent > 100) return -1;
    return percent;
#endif
}
#include <ncurses.h>
#include <stdlib.h>
#include <string.h>



#define MAX_APPS 256
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
    // Parse apps array robustly
    // Find the start of the array
    char *array_start = strchr(buf, '[');
    if (!array_start) return app_count > 0;
    p = array_start;
    while ((p = strstr(p, "{\"name\"")) && app_count < MAX_APPS) {
        char *n = strstr(p, ":");
        if (!n) break;
        n++;
        while (*n == ' ' || *n == '"') n++;
        char *ne = strchr(n, '"');
        if (!ne) break;
        int nlen = ne-n;
        strncpy(apps[app_count].name, n, nlen > APP_NAME_LEN-1 ? APP_NAME_LEN-1 : nlen);
        apps[app_count].name[nlen > APP_NAME_LEN-1 ? APP_NAME_LEN-1 : nlen] = 0;
        char *a = strstr(ne, "\"alias\"");
        if (!a) break;
        a = strchr(a, ':');
        if (!a) break;
        a++;
        while (*a == ' ' || *a == '"') a++;
        char *ae = strchr(a, '"');
        if (!ae) break;
        int alen = ae-a;
        strncpy(apps[app_count].alias, a, alen > APP_ALIAS_LEN-1 ? APP_ALIAS_LEN-1 : alen);
        apps[app_count].alias[alen > APP_ALIAS_LEN-1 ? APP_ALIAS_LEN-1 : alen] = 0;
        app_count++;
        // Move p to after this app object
        p = strchr(ae, '}');
        if (!p) break;
        p++;
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

void draw_menu(int highlight, bool in_settings, int scroll_offset) {
    clear();
    int max_y, max_x;
    getmaxyx(stdscr, max_y, max_x);
    int header_lines = in_settings ? 13 : 2;
    int visible_lines = max_y - header_lines;
    int battery = get_battery_percent();
    char header[128];
    if (battery >= 0) {
        snprintf(header, sizeof(header), "Aero App Center (TUI) | Battery: %d%%", battery);
    } else {
        snprintf(header, sizeof(header), "Aero App Center (TUI)");
    }
    if (in_settings) {
        mvprintw(0, 2, "%s", header);
        mvprintw(1, 2, "Use arrow keys, Enter to select, q to return.");
        if (highlight == 0) attron(COLOR_PAIR(3));
        mvprintw(3, 4, "Update Aero");
        if (highlight == 0) attroff(COLOR_PAIR(3));
        if (highlight == 1) attron(COLOR_PAIR(3));
        mvprintw(4, 4, "Edit App List");
        if (highlight == 1) attroff(COLOR_PAIR(3));
        if (highlight == 2) attron(COLOR_PAIR(3));
        mvprintw(5, 4, "Back");
        if (highlight == 2) attroff(COLOR_PAIR(3));
        if (highlight == 3) attron(COLOR_PAIR(3));
        mvprintw(7, 4, "Special Key Mode: %s", strcmp(aero_settings.nav_mode, "function_keys") == 0 ? "Function Keys" : "Letters");
        if (highlight == 3) attroff(COLOR_PAIR(3));
        mvprintw(8, 4, "(Toggle and save to app-list.txt)");
        mvprintw(10, 2, "App Color: fg=%s bg=%s", aero_settings.app_fg, aero_settings.app_bg);
        mvprintw(11, 2, "Selected Color: fg=%s bg=%s", aero_settings.sel_fg, aero_settings.sel_bg);
        mvprintw(12, 2, "Edit app-list.txt to change colors.");
    } else {
        mvprintw(0, 2, "%s", header);
        if (strcmp(aero_settings.nav_mode, "function_keys") == 0) {
            mvprintw(1, 2, "F1: Quit, F2: Settings, arrows to navigate, Enter to select");
        } else {
            mvprintw(1, 2, "Use arrow keys, Enter to select, q to quit, s for settings.");
        }
        int start = scroll_offset;
        int end = start + visible_lines;
        if (end > app_count) end = app_count;
        for (int i = start; i < end; ++i) {
            int y = i - start + 2;
            if (i == highlight) {
                attron(COLOR_PAIR(2));
                mvprintw(y, 4, "%s", apps[i].name);
                attroff(COLOR_PAIR(2));
            } else {
                attron(COLOR_PAIR(1));
                mvprintw(y, 4, "%s", apps[i].name);
                attroff(COLOR_PAIR(1));
            }
        }
        // Show scroll indicators if needed
        if (scroll_offset > 0) mvprintw(2, max_x-3, "^");
        if (end < app_count) mvprintw(max_y-1, max_x-3, "v");
    }
    refresh();
}

void save_settings(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) {
        mvprintw(0, 0, "[Aero] Error: Cannot open %s for reading.", filename);
        getch();
        return;
    }
    char buf[4096];
    size_t len = fread(buf, 1, sizeof(buf)-1, f);
    buf[len] = 0;
    fclose(f);
    // Remove any old settings object
    char *apps_start = strchr(buf, '[');
    if (!apps_start) {
        mvprintw(0, 0, "[Aero] Error: Malformed app-list.txt (no app array).\n");
        getch();
        return;
    }
    FILE *out = fopen(filename, "w");
    if (!out) {
        clear();
        mvprintw(0, 0, "[Aero] Error: Cannot write to %s.\nSettings not saved.\nRun Aero as root or edit with sudo.", filename);
        mvprintw(2, 0, "Press any key to continue...");
        refresh();
        getch();
        return;
    }
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
    int scroll_offset = 0;
    int max_y, max_x;
    getmaxyx(stdscr, max_y, max_x);
    int header_lines = 2;
    int visible_lines = max_y - header_lines;
    draw_menu(highlight, in_settings, scroll_offset);
    while (1) {
        ch = getch();
        if (!in_settings) {
            if ((strcmp(aero_settings.nav_mode, "function_keys") == 0 && ch == KEY_F(1)) || (strcmp(aero_settings.nav_mode, "letters") == 0 && ch == 'q')) break;
            if ((strcmp(aero_settings.nav_mode, "function_keys") == 0 && ch == KEY_F(2)) || (strcmp(aero_settings.nav_mode, "letters") == 0 && ch == 's')) {
                in_settings = true;
                settings_highlight = 0;
                draw_menu(settings_highlight, in_settings, 0);
                continue;
            }
        } else {
            if ((strcmp(aero_settings.nav_mode, "function_keys") == 0 && ch == KEY_F(1)) || (strcmp(aero_settings.nav_mode, "letters") == 0 && ch == 'q')) {
                in_settings = false;
                draw_menu(highlight, in_settings, scroll_offset);
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
                        printf("Opening app-list.txt in nano (sudo)...\n");
                        system("sudo nano /aero/app-list.txt");
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
            draw_menu(settings_highlight, in_settings, 0);
            continue;
        }
        getmaxyx(stdscr, max_y, max_x);
        visible_lines = max_y - header_lines;
        int last_visible = scroll_offset + visible_lines - 1;
        switch (ch) {
            case KEY_UP:
                if (highlight > 0) --highlight;
                break;
            case KEY_DOWN:
                if (highlight < app_count - 1) ++highlight;
                break;
            case KEY_NPAGE: // Page Down
                highlight += visible_lines;
                if (highlight >= app_count) highlight = app_count - 1;
                break;
            case KEY_PPAGE: // Page Up
                highlight -= visible_lines;
                if (highlight < 0) highlight = 0;
                break;
            case '\n':
                endwin();
                system("clear");
                char cmd[APP_ALIAS_LEN + 32];
                snprintf(cmd, sizeof(cmd), "%s", apps[highlight].alias);
                system(cmd);
                initscr();
                clear();
                noecho();
                cbreak();
                keypad(stdscr, TRUE);
                break;
        }
        // Adjust scroll_offset to keep highlight visible
        if (highlight < scroll_offset) scroll_offset = highlight;
        if (highlight >= scroll_offset + visible_lines) scroll_offset = highlight - visible_lines + 1;
        draw_menu(highlight, in_settings, scroll_offset);
    }
    endwin();
    return 0;
}
