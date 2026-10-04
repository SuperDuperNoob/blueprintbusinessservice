#!/usr/bin/env python3
"""
Generate a clean, highly legible, ultra-responsive web application
for Coach Adib & Blueprint Business Service.
Supports 4 Core Programs:
1. Blueprint Business Owner (BBO)
2. Seni Closing Customer (SCC)
3. Blueprint Business Service (BBS)
4. Live Recording (LIVE)

Features:
- Clean, user-friendly Inter typography for notes, courses, and scripts
- Day (Light) and Night (Dark) themes with smooth toggle & persistence
- Program tab navigation with active status, progress bars, and badges
- Multi-tier accordion navigation: Program -> Course -> Chapter -> Modules
- Full Bunny CDN HD video stream + Bunny Embed player toggle with speed controls
- Distraction-free Focus mode, Theater mode, and custom shortcuts
- 100% offline pure JS confetti celebration & toast notifications
- Interactive quizzes with instant explanation reveals
- Quick keyboard navigation ([, ], N, P, Space, F, M, B, D, T, /, ?)
"""
import json
import os

def build_offline_site():
    os.makedirs("offline_site", exist_ok=True)
    with open("bbs_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    programs = sorted(data.get("Program", []), key=lambda x: x.get("order", 0))
    levels = sorted(data.get("Level", []), key=lambda x: x.get("level_number", 0))
    courses = sorted(data.get("Course", []), key=lambda x: (x.get("order", 0), x.get("level_number", 0)))
    chapters = sorted(data.get("Chapter", []), key=lambda x: x.get("order", 0))
    modules = sorted(data.get("Module", []), key=lambda x: (x.get("order", 0), x.get("level_number", 0)))

    # Save CNAME
    with open("offline_site/CNAME", "w", encoding="utf-8") as f:
        f.write("bbs.archxry.space\n")

    # Save data.js
    with open("offline_site/data.js", "w", encoding="utf-8") as f:
        f.write("window.BBS_DATA = " + json.dumps({
            "programs": programs,
            "levels": levels,
            "courses": courses,
            "chapters": chapters,
            "modules": modules
        }, ensure_ascii=False) + ";\n")

    html_content = r"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=1.0, user-scalable=no">
  <meta name="referrer" content="origin-when-cross-origin">
  <title>Coach Adib · Video & Business Knowledge Hub</title>
  <script src="marked.min.js"></script>
  <script src="hls.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --accent-brand: #ff5a00;
      --accent-brand-hover: #ff7324;
      --accent-brand-glow: rgba(255, 90, 0, 0.32);
      --accent-emerald: #10b981;
      --accent-emerald-glow: rgba(16, 185, 129, 0.28);
      --accent-cyan: #06b6d4;
      --accent-rose: #f43f5e;
      --accent-amber: #f59e0b;
      --accent-purple: #8b5cf6;
      
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-xl: 18px;
      --sidebar-width: 390px;
      --topbar-height: 60px;
    }

    /* Dark / Night Theme (Default) */
    html.dark {
      --bg-base: #060911;
      --bg-surface: #0c1220;
      --bg-card: #131c31;
      --bg-card-hover: #192642;
      --bg-card-active: #1d2d4f;
      --bg-elevated: #1e293b;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-medium: rgba(255, 255, 255, 0.14);
      --border-focus: rgba(255, 90, 0, 0.55);
      
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-tertiary: #64748b;
      --text-muted: #475569;

      --topbar-bg: rgba(6, 9, 17, 0.85);
      --sidebar-header-bg: rgba(12, 18, 32, 0.95);
      --level-tabs-bg: rgba(6, 9, 17, 0.85);
      --quiz-card-bg: rgba(6, 9, 17, 0.65);
      --table-th-bg: rgba(6, 9, 17, 0.85);
      --code-bg: rgba(6, 9, 17, 0.95);
      --upcoming-bg: linear-gradient(135deg, rgba(245, 158, 11, 0.09) 0%, rgba(15, 23, 42, 0.95) 100%);
    }

    /* Light / Day Theme */
    html.light {
      --bg-base: #f1f5f9;
      --bg-surface: #ffffff;
      --bg-card: #ffffff;
      --bg-card-hover: #f8fafc;
      --bg-card-active: #e2e8f0;
      --bg-elevated: #ffffff;
      --border-subtle: rgba(0, 0, 0, 0.08);
      --border-medium: rgba(0, 0, 0, 0.15);
      --border-focus: rgba(255, 90, 0, 0.6);
      
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-tertiary: #64748b;
      --text-muted: #94a3b8;

      --topbar-bg: rgba(255, 255, 255, 0.9);
      --sidebar-header-bg: rgba(255, 255, 255, 0.96);
      --level-tabs-bg: rgba(241, 245, 249, 0.9);
      --quiz-card-bg: #f8fafc;
      --table-th-bg: #f1f5f9;
      --code-bg: #e2e8f0;
      --upcoming-bg: linear-gradient(135deg, rgba(254, 243, 199, 0.6) 0%, #ffffff 100%);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    html, body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg-base);
      color: var(--text-primary);
      height: 100%;
      width: 100%;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.25s ease, color 0.25s ease;
    }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(140, 140, 140, 0.2); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(140, 140, 140, 0.4); }

    /* App Shell */
    #app-shell {
      display: flex;
      height: 100vh;
      height: 100dvh;
      width: 100vw;
      overflow: hidden;
      position: relative;
    }

    /* Sidebar */
    #sidebar {
      width: var(--sidebar-width);
      min-width: var(--sidebar-width);
      max-width: var(--sidebar-width);
      height: 100%;
      background: var(--bg-surface);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      z-index: 50;
      transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.25s ease;
      overflow: hidden;
    }
    #sidebar.focus-hidden {
      transform: translateX(-100%);
      margin-right: calc(-1 * var(--sidebar-width));
    }

    /* Sidebar Header */
    .sidebar-header {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--sidebar-header-bg);
      backdrop-filter: blur(12px);
      flex-shrink: 0;
    }
    .brand-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .brand-logo {
      width: 34px;
      height: 34px;
      background: linear-gradient(135deg, #ff5a00, #ff8c00);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.88rem;
      color: #ffffff;
      box-shadow: 0 4px 12px var(--accent-brand-glow);
    }
    .brand-info h2 {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.2;
    }
    .brand-info p {
      font-size: 0.72rem;
      color: var(--text-tertiary);
      font-family: 'JetBrains Mono', monospace;
    }
    .overall-badge {
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 4px 9px;
      background: rgba(255, 90, 0, 0.12);
      border: 1px solid rgba(255, 90, 0, 0.25);
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--accent-brand);
      font-family: 'JetBrains Mono', monospace;
    }

    .btn-close-sidebar {
      display: none;
      background: transparent;
      border: none;
      color: var(--text-secondary);
      padding: 6px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 1.1rem;
    }

    /* Program / Level Tabs Bar */
    .level-tabs-container {
      overflow-x: auto;
      background: var(--level-tabs-bg);
      border-bottom: 1px solid var(--border-subtle);
      flex-shrink: 0;
      -webkit-overflow-scrolling: touch;
    }
    .level-tabs {
      display: flex;
      padding: 8px 10px;
      gap: 6px;
      width: max-content;
    }
    .level-tab {
      padding: 6px 12px;
      border-radius: var(--radius-md);
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-secondary);
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.18s ease;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .level-tab:hover { background: rgba(140, 140, 140, 0.1); color: var(--text-primary); }
    .level-tab.active {
      background: linear-gradient(135deg, rgba(255,90,0,0.22), rgba(255,90,0,0.08));
      color: #ff5a00;
      border-color: rgba(255,90,0,0.4);
      box-shadow: 0 2px 12px rgba(255,90,0,0.15);
      font-weight: 700;
    }
    .level-tab-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: rgba(140, 140, 140, 0.3);
    }
    .level-tab.active .level-tab-dot {
      background: var(--accent-brand);
      box-shadow: 0 0 6px var(--accent-brand);
    }
    .level-tab.all-done .level-tab-dot {
      background: var(--accent-emerald);
      box-shadow: 0 0 6px var(--accent-emerald);
    }

    /* Search & Filter Section */
    .search-section {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 8px;
      flex-shrink: 0;
    }
    .search-input-wrap {
      position: relative;
      display: flex;
      align-items: center;
    }
    .search-input {
      width: 100%;
      padding: 7px 30px 7px 32px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      color: var(--text-primary);
      font-size: 0.82rem;
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s ease, background 0.15s ease;
    }
    .search-input:focus {
      border-color: var(--accent-brand);
      background: var(--bg-elevated);
    }
    .search-icon {
      position: absolute;
      left: 10px;
      width: 14px;
      height: 14px;
      color: var(--text-tertiary);
      pointer-events: none;
    }
    .search-clear-btn {
      position: absolute;
      right: 8px;
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      font-size: 0.75rem;
      cursor: pointer;
      padding: 2px 4px;
      display: none;
    }
    .search-clear-btn:hover { color: var(--text-primary); }

    .filter-pills {
      display: flex;
      gap: 4px;
      overflow-x: auto;
      padding-bottom: 2px;
    }
    .filter-pill {
      padding: 4px 8px;
      border-radius: 999px;
      border: 1px solid var(--border-subtle);
      background: transparent;
      color: var(--text-tertiary);
      font-size: 0.72rem;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }
    .filter-pill:hover {
      color: var(--text-primary);
      border-color: var(--border-medium);
    }
    .filter-pill.active {
      background: var(--bg-card-active);
      color: var(--text-primary);
      border-color: rgba(255, 90, 0, 0.4);
      font-weight: 600;
    }

    /* Program / Level Meta Bar */
    .level-meta-bar {
      padding: 8px 14px;
      background: rgba(140, 140, 140, 0.04);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    .level-title-display {
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 190px;
    }
    .meta-right-tools {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .btn-accordion-toggle {
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      font-size: 0.7rem;
      cursor: pointer;
      font-weight: 500;
      padding: 2px 4px;
      border-radius: var(--radius-sm);
    }
    .btn-accordion-toggle:hover { color: var(--text-primary); }
    .level-prog-wrap {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.72rem;
      color: var(--text-tertiary);
    }
    .prog-bar-mini {
      width: 44px;
      height: 5px;
      background: rgba(140, 140, 140, 0.2);
      border-radius: 999px;
      overflow: hidden;
    }
    .prog-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #ff5a00, #10b981);
      border-radius: 999px;
      transition: width 0.3s ease;
    }

    /* Navigation List */
    .nav-list {
      flex: 1;
      overflow-y: auto;
      padding: 10px 8px 40px 8px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    /* Course Group Accordion */
    .course-group {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      overflow: hidden;
      transition: border-color 0.15s ease;
    }
    .course-group:hover {
      border-color: var(--border-medium);
    }
    .course-header {
      padding: 10px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      user-select: none;
      font-weight: 700;
      font-size: 0.82rem;
      color: var(--text-primary);
      background: rgba(140, 140, 140, 0.03);
    }
    .course-header-left {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
      overflow: hidden;
    }
    .course-chevron {
      font-size: 0.65rem;
      color: var(--text-tertiary);
      transition: transform 0.2s ease;
    }
    .course-group.collapsed .course-chevron {
      transform: rotate(-90deg);
    }
    .course-group.collapsed .course-body {
      display: none;
    }
    .course-release-tag {
      font-size: 0.65rem;
      font-family: 'JetBrains Mono', monospace;
      color: var(--accent-amber);
      background: rgba(245, 158, 11, 0.12);
      padding: 2px 6px;
      border-radius: var(--radius-sm);
      margin-left: 6px;
    }

    .course-body {
      padding: 4px 6px 8px 6px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    /* Chapter Group Accordion */
    .chapter-group {
      border-left: 2px solid var(--border-subtle);
      margin-left: 8px;
      padding-left: 6px;
      margin-top: 4px;
      margin-bottom: 4px;
    }
    .chapter-header {
      padding: 5px 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      user-select: none;
      font-weight: 600;
      font-size: 0.77rem;
      color: var(--text-secondary);
      border-radius: var(--radius-sm);
    }
    .chapter-header:hover {
      background: rgba(140, 140, 140, 0.06);
      color: var(--text-primary);
    }
    .chapter-title-text {
      display: flex;
      align-items: center;
      gap: 6px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .chapter-chevron {
      font-size: 0.6rem;
      color: var(--text-tertiary);
      transition: transform 0.2s ease;
    }
    .chapter-group.collapsed .chapter-chevron {
      transform: rotate(-90deg);
    }
    .chapter-group.collapsed .chapter-lessons {
      display: none;
    }
    .chapter-count {
      font-size: 0.68rem;
      color: var(--text-tertiary);
      font-family: 'JetBrains Mono', monospace;
    }

    .chapter-lessons {
      display: flex;
      flex-direction: column;
      gap: 2px;
      padding-top: 2px;
    }

    /* Lesson Module Item */
    .lesson-item {
      padding: 7px 10px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      transition: all 0.12s ease;
      font-size: 0.78rem;
      color: var(--text-secondary);
      text-decoration: none;
      gap: 8px;
      user-select: none;
    }
    .lesson-item:hover {
      background: var(--bg-card-hover);
      color: var(--text-primary);
    }
    .lesson-item.active {
      background: linear-gradient(135deg, rgba(255, 90, 0, 0.18), rgba(255, 90, 0, 0.08));
      color: var(--accent-brand);
      font-weight: 600;
      border-left: 3px solid var(--accent-brand);
    }
    .lesson-item.completed .lesson-title-text {
      color: var(--text-muted);
    }
    .lesson-item.active.completed .lesson-title-text {
      color: var(--accent-brand);
    }
    .lesson-left {
      display: flex;
      align-items: center;
      gap: 7px;
      overflow: hidden;
      flex: 1;
    }
    .lesson-icon {
      font-size: 0.8rem;
      flex-shrink: 0;
      opacity: 0.75;
    }
    .lesson-title-text {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .lesson-right-badges {
      display: flex;
      align-items: center;
      gap: 4px;
      flex-shrink: 0;
    }
    .lesson-badge-pill {
      font-size: 0.65rem;
      padding: 1px 5px;
      border-radius: var(--radius-sm);
      font-weight: 500;
    }
    .pill-video {
      background: rgba(16, 185, 129, 0.14);
      color: var(--accent-emerald);
      border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .pill-notes {
      background: rgba(6, 182, 212, 0.14);
      color: var(--accent-cyan);
      border: 1px solid rgba(6, 182, 212, 0.25);
    }
    .pill-upcoming {
      background: rgba(245, 158, 11, 0.14);
      color: var(--accent-amber);
      border: 1px solid rgba(245, 158, 11, 0.25);
    }
    .lesson-bookmark-icon {
      color: var(--accent-amber);
      font-size: 0.75rem;
    }

    /* Main Content Area */
    #main-content {
      flex: 1;
      height: 100%;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      background: var(--bg-base);
      transition: background-color 0.25s ease;
      position: relative;
    }

    /* Topbar */
    .topbar {
      height: var(--topbar-height);
      min-height: var(--topbar-height);
      padding: 0 20px;
      border-bottom: 1px solid var(--border-subtle);
      background: var(--topbar-bg);
      backdrop-filter: blur(16px);
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 40;
    }
    .topbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
      overflow: hidden;
    }
    .btn-topbar-icon {
      background: transparent;
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      width: 34px;
      height: 34px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
      font-size: 0.9rem;
    }
    .btn-topbar-icon:hover {
      background: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--border-medium);
    }
    .btn-hamburger {
      display: none;
    }

    .breadcrumb-nav {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.82rem;
      color: var(--text-tertiary);
      overflow: hidden;
      white-space: nowrap;
    }
    .breadcrumb-item {
      color: var(--text-secondary);
      text-overflow: ellipsis;
      overflow: hidden;
    }
    .breadcrumb-sep {
      color: var(--text-muted);
    }
    .breadcrumb-current {
      color: var(--text-primary);
      font-weight: 600;
      text-overflow: ellipsis;
      overflow: hidden;
    }

    .topbar-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .btn {
      padding: 7px 14px;
      border-radius: var(--radius-md);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      border: 1px solid transparent;
      transition: all 0.15s ease;
    }
    .btn-primary {
      background: var(--accent-brand);
      color: #ffffff;
      box-shadow: 0 2px 10px var(--accent-brand-glow);
    }
    .btn-primary:hover {
      background: var(--accent-brand-hover);
      transform: translateY(-1px);
    }
    .btn-secondary {
      background: var(--bg-card);
      border-color: var(--border-subtle);
      color: var(--text-primary);
    }
    .btn-secondary:hover {
      background: var(--bg-card-hover);
      border-color: var(--border-medium);
    }
    .btn-done {
      background: rgba(16, 185, 129, 0.15);
      border-color: rgba(16, 185, 129, 0.35);
      color: var(--accent-emerald);
    }
    .btn-bookmarked {
      color: var(--accent-amber);
      border-color: rgba(245, 158, 11, 0.4);
      background: rgba(245, 158, 11, 0.12);
    }

    /* Content Body Container */
    .content-container {
      max-width: 1040px;
      width: 100%;
      margin: 0 auto;
      padding: 24px 24px 80px 24px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    /* Lesson Hero Header */
    .lesson-hero {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 22px 26px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    .lesson-hero-header-row {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
    }
    .lesson-hero-title {
      font-size: 1.55rem;
      font-weight: 800;
      color: var(--text-primary);
      line-height: 1.25;
      letter-spacing: -0.02em;
    }
    .hero-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .hero-tag {
      padding: 4px 10px;
      border-radius: var(--radius-sm);
      font-size: 0.72rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
      letter-spacing: 0.02em;
    }
    .tag-level { background: rgba(255, 90, 0, 0.12); color: var(--accent-brand); border: 1px solid rgba(255, 90, 0, 0.25); }
    .tag-duration { background: rgba(140, 140, 140, 0.12); color: var(--text-secondary); border: 1px solid var(--border-subtle); }
    .tag-video-live { background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); border: 1px solid rgba(16, 185, 129, 0.3); }
    .tag-notes-live { background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan); border: 1px solid rgba(6, 182, 212, 0.3); }
    .tag-upcoming { background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); border: 1px solid rgba(245, 158, 11, 0.3); }
    .tag-req { background: rgba(139, 92, 246, 0.15); color: var(--accent-purple); border: 1px solid rgba(139, 92, 246, 0.3); }

    /* Video Player Card */
    .video-hero-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: 0 6px 30px rgba(0, 0, 0, 0.12);
      transition: all 0.3s ease;
    }
    .video-hero-card.theater-mode {
      position: relative;
      max-width: 100%;
      border-radius: var(--radius-md);
    }
    .video-card-topbar {
      padding: 10px 16px;
      background: rgba(140, 140, 140, 0.04);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .video-stream-badge {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.74rem;
      font-weight: 600;
      color: var(--accent-emerald);
      font-family: 'JetBrains Mono', monospace;
    }
    .stream-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--accent-emerald);
      box-shadow: 0 0 8px var(--accent-emerald);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .video-controls-quick {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .speed-btn, .jump-btn, .player-toggle-btn {
      padding: 3px 8px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: transparent;
      color: var(--text-secondary);
      font-size: 0.7rem;
      font-family: 'JetBrains Mono', monospace;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.15s ease;
    }
    .speed-btn:hover, .jump-btn:hover, .player-toggle-btn:hover {
      background: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--border-medium);
    }
    .speed-btn.active {
      background: var(--accent-brand);
      color: #ffffff;
      border-color: var(--accent-brand);
    }

    .video-wrapper {
      position: relative;
      width: 100%;
      padding-top: 56.25%; /* 16:9 Aspect Ratio */
      background: #000000;
    }
    .video-wrapper video, .video-wrapper iframe {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border: none;
    }

    /* Production / Upcoming Notice */
    .upcoming-card {
      background: var(--upcoming-bg);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: var(--radius-lg);
      padding: 32px 24px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 14px;
    }
    .upcoming-icon {
      font-size: 2.2rem;
    }
    .upcoming-title {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--accent-amber);
    }
    .upcoming-desc {
      font-size: 0.88rem;
      color: var(--text-secondary);
      max-width: 520px;
      line-height: 1.5;
    }
    .upcoming-actions {
      display: flex;
      gap: 10px;
      margin-top: 8px;
      flex-wrap: wrap;
      justify-content: center;
    }

    /* Notes & Study Material */
    .study-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 28px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
      line-height: 1.68;
    }
    .study-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 14px;
      margin-bottom: 20px;
    }
    .study-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* Clean Markdown Typography (Inter) */
    .markdown-body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 0.95rem;
      color: var(--text-primary);
      line-height: 1.72;
      letter-spacing: -0.011em;
    }
    .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 {
      color: var(--text-primary);
      font-weight: 700;
      margin-top: 1.5em;
      margin-bottom: 0.6em;
      line-height: 1.3;
    }
    .markdown-body h1 { font-size: 1.45rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 6px; }
    .markdown-body h2 { font-size: 1.22rem; }
    .markdown-body h3 { font-size: 1.05rem; }
    .markdown-body p { margin-bottom: 1em; }
    .markdown-body ul, .markdown-body ol {
      margin-left: 1.4em;
      margin-bottom: 1em;
    }
    .markdown-body li {
      margin-bottom: 0.35em;
    }
    .markdown-body blockquote {
      border-left: 3px solid var(--accent-brand);
      padding: 8px 16px;
      margin: 1.2em 0;
      background: rgba(255, 90, 0, 0.06);
      border-radius: 0 var(--radius-md) var(--radius-md) 0;
      color: var(--text-secondary);
      font-style: italic;
    }
    .markdown-body code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.84rem;
      padding: 2px 6px;
      background: var(--code-bg);
      border-radius: var(--radius-sm);
      color: var(--accent-brand);
    }
    .markdown-body pre {
      background: var(--code-bg);
      padding: 14px 18px;
      border-radius: var(--radius-md);
      overflow-x: auto;
      margin: 1.2em 0;
      border: 1px solid var(--border-subtle);
    }
    .markdown-body pre code {
      background: transparent;
      padding: 0;
      color: var(--text-primary);
    }
    .markdown-body table {
      width: 100%;
      border-collapse: collapse;
      margin: 1.2em 0;
      font-size: 0.88rem;
    }
    .markdown-body th, .markdown-body td {
      border: 1px solid var(--border-subtle);
      padding: 9px 13px;
      text-align: left;
    }
    .markdown-body th {
      background: var(--table-th-bg);
      font-weight: 600;
      color: var(--text-primary);
    }
    .markdown-body tr:nth-child(even) {
      background: rgba(140, 140, 140, 0.03);
    }
    .markdown-body hr {
      border: none;
      border-top: 1px solid var(--border-subtle);
      margin: 2em 0;
    }

    /* Interactive Quizzes */
    .quiz-section {
      margin-top: 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .quiz-item-card {
      background: var(--quiz-card-bg);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 16px 20px;
    }
    .quiz-question-title {
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 12px;
    }
    .quiz-options-list {
      display: flex;
      flex-direction: column;
      gap: 7px;
    }
    .quiz-opt-btn {
      padding: 9px 14px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: var(--bg-card);
      color: var(--text-secondary);
      font-size: 0.84rem;
      font-family: inherit;
      cursor: pointer;
      text-align: left;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .quiz-opt-btn:hover {
      background: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--border-medium);
    }
    .quiz-opt-btn.correct {
      background: rgba(16, 185, 129, 0.18);
      border-color: var(--accent-emerald);
      color: var(--accent-emerald);
      font-weight: 600;
    }
    .quiz-opt-btn.wrong {
      background: rgba(244, 63, 94, 0.18);
      border-color: var(--accent-rose);
      color: var(--accent-rose);
    }
    .quiz-feedback-box {
      margin-top: 10px;
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      font-size: 0.82rem;
      background: rgba(16, 185, 129, 0.08);
      border: 1px solid rgba(16, 185, 129, 0.25);
      color: var(--text-primary);
      display: none;
    }

    /* Lesson Footer Navigation */
    .lesson-footer-nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding-top: 12px;
    }

    /* Toast Notification */
    #toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--bg-elevated);
      color: var(--text-primary);
      padding: 10px 18px;
      border-radius: var(--radius-md);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-medium);
      font-size: 0.84rem;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
      z-index: 1000;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      pointer-events: none;
    }
    #toast.show {
      transform: translateY(0);
      opacity: 1;
    }

    /* Confetti Canvas */
    #confetti-canvas {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 999;
    }

    /* Keyboard Shortcuts Modal */
    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 200;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }
    .modal-backdrop.open {
      opacity: 1;
      pointer-events: auto;
    }
    .shortcuts-dialog {
      background: var(--bg-card);
      border: 1px solid var(--border-medium);
      border-radius: var(--radius-lg);
      padding: 24px;
      max-width: 480px;
      width: 90%;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }
    .shortcuts-dialog h3 {
      font-size: 1.1rem;
      font-weight: 700;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .shortcut-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid var(--border-subtle);
      font-size: 0.85rem;
    }
    .key-badge {
      background: var(--bg-elevated);
      border: 1px solid var(--border-medium);
      border-radius: var(--radius-sm);
      padding: 2px 7px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      font-weight: 600;
      box-shadow: 0 2px 0 rgba(0,0,0,0.2);
    }

    /* Responsive Breakdown */
    @media (max-width: 960px) {
      #sidebar {
        position: fixed;
        left: 0;
        top: 0;
        height: 100%;
        transform: translateX(-100%);
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.3);
      }
      #sidebar.mobile-open {
        transform: translateX(0);
      }
      #mobile-backdrop {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(2px);
        z-index: 45;
      }
      #mobile-backdrop.active {
        display: block;
      }
      .btn-hamburger {
        display: flex;
      }
      .btn-close-sidebar {
        display: block;
      }
      .content-container {
        padding: 16px 14px 60px 14px;
      }
      .btn-text-hide {
        display: none;
      }
    }
  </style>
</head>
<body>
  <canvas id="confetti-canvas"></canvas>
  <div id="toast">
    <span id="toast-icon">⚡</span>
    <span id="toast-msg">Notification</span>
  </div>

  <div id="shortcuts-modal" class="modal-backdrop" onclick="closeShortcutsModal(event)">
    <div class="shortcuts-dialog" onclick="event.stopPropagation()">
      <h3>
        <span>⌨️ Keyboard Shortcuts</span>
        <button onclick="toggleShortcutsModal()" style="background:transparent;border:none;color:var(--text-tertiary);cursor:pointer;font-size:1.1rem;">✕</button>
      </h3>
      <div class="shortcut-row"><span>Next Lesson</span><span class="key-badge">] or N</span></div>
      <div class="shortcut-row"><span>Previous Lesson</span><span class="key-badge">[ or P</span></div>
      <div class="shortcut-row"><span>Mark Complete</span><span class="key-badge">M</span></div>
      <div class="shortcut-row"><span>Bookmark Lesson</span><span class="key-badge">B</span></div>
      <div class="shortcut-row"><span>Toggle Day / Night Mode</span><span class="key-badge">D</span></div>
      <div class="shortcut-row"><span>Theater Video Mode</span><span class="key-badge">T</span></div>
      <div class="shortcut-row"><span>Focus Mode (Hide Sidebar)</span><span class="key-badge">F</span></div>
      <div class="shortcut-row"><span>Quick Search</span><span class="key-badge">/</span></div>
      <div class="shortcut-row"><span>Shortcuts Guide</span><span class="key-badge">?</span></div>
    </div>
  </div>

  <div id="app-shell">
    <!-- Backdrop Overlay for Mobile -->
    <div id="mobile-backdrop" onclick="closeMobileSidebar()"></div>

    <!-- Sidebar / Drawer -->
    <aside id="sidebar">
      <div class="sidebar-header">
        <div class="brand-group">
          <div class="brand-logo">CA</div>
          <div class="brand-info">
            <h2>Coach Adib</h2>
            <p>Knowledge Studio</p>
          </div>
        </div>
        <div class="overall-badge" id="overall-progress-badge" title="Overall platform progress">
          <span>⚡</span><span id="overall-pct-text">0%</span>
        </div>
        <button class="btn-close-sidebar" onclick="closeMobileSidebar()" aria-label="Close sidebar">✕</button>
      </div>

      <!-- Program / Level Tabs Horizontal Scroll -->
      <div class="level-tabs-container">
        <div class="level-tabs" id="level-tabs"></div>
      </div>

      <!-- Search & Readiness Filter -->
      <div class="search-section">
        <div class="search-input-wrap">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" id="search-input" class="search-input" placeholder="Search 408 lessons, notes (/)..." />
          <button class="search-clear-btn" id="search-clear-btn" onclick="clearSearch()">✕</button>
        </div>
        <div class="filter-pills">
          <button class="filter-pill active" id="filter-all" onclick="setFilter('all')">All (<span id="count-all">0</span>)</button>
          <button class="filter-pill" id="filter-ready" onclick="setFilter('ready')">⚡ Video (<span id="count-ready">0</span>)</button>
          <button class="filter-pill" id="filter-done" onclick="setFilter('done')">✓ Done (<span id="count-done">0</span>)</button>
          <button class="filter-pill" id="filter-saved" onclick="setFilter('saved')">⭐ Saved (<span id="count-saved">0</span>)</button>
        </div>
      </div>

      <!-- Active Program / Level Progress & Accordion Actions -->
      <div class="level-meta-bar">
        <span class="level-title-display" id="level-active-title">Program Overview</span>
        <div class="meta-right-tools">
          <button class="btn-accordion-toggle" id="btn-toggle-accordions" onclick="toggleAllAccordions()">Collapse All</button>
          <div class="level-prog-wrap">
            <div class="prog-bar-mini"><div class="prog-bar-fill" id="level-prog-fill" style="width: 0%;"></div></div>
            <span id="level-prog-text" style="font-family:'JetBrains Mono',monospace;">0/0</span>
          </div>
        </div>
      </div>

      <!-- Navigation Tree -->
      <div class="nav-list" id="nav-list"></div>
    </aside>

    <!-- Main Content Area -->
    <main id="main-content">
      <header class="topbar">
        <div class="topbar-left">
          <button class="btn-topbar-icon btn-hamburger" onclick="openMobileSidebar()" aria-label="Open lessons menu">☰</button>
          <button class="btn-topbar-icon" id="btn-focus-toggle" onclick="toggleFocusMode()" title="Toggle Focus Mode (F)">⇸</button>
          <div class="breadcrumb-nav" id="breadcrumb">
            <span>Select a lesson</span>
          </div>
        </div>
        <div class="topbar-actions">
          <!-- Day / Night Mode Toggle Button -->
          <button class="btn-topbar-icon" id="btn-theme-toggle" onclick="toggleTheme()" title="Toggle Day / Night Mode (D)">
            <span id="theme-icon">🌙</span>
          </button>
          <button class="btn btn-secondary" id="btn-bookmark-action" onclick="toggleBookmark()" title="Bookmark Lesson (B)">
            <span id="bookmark-icon">☆</span> <span class="btn-text-hide">Save</span>
          </button>
          <button class="btn btn-secondary" onclick="toggleTheaterMode()" title="Theater Mode (T)">
            <span>⛶</span>
          </button>
          <button class="btn btn-primary" id="btn-complete-action" onclick="toggleComplete()" title="Mark Done (M)">
            <span>✓</span> <span class="btn-done-text btn-text-hide">Mark Done</span>
          </button>
          <button class="btn-topbar-icon" onclick="toggleShortcutsModal()" title="Keyboard Shortcuts (?)">?</button>
        </div>
      </header>

      <div class="content-container" id="content-container"></div>
    </main>
  </div>

  <script src="data.js"></script>
  <script>
    let activeHls = null;
    let currentSpeed = 1;
    let isTheater = false;
    let isFocusMode = false;
    let activeFilter = 'all';
    let allAccordionsCollapsed = false;
    let currentTheme = localStorage.getItem('bbs_theme') || 'dark';
    let playerMode = localStorage.getItem('bbs_player_mode') || 'iframe'; // default 'iframe' for 100% universal reliability

    const { programs = [], levels = [], courses = [], chapters = [], modules = [] } = window.BBS_DATA || {};
    const hasPrograms = Boolean(programs && programs.length > 0);

    let currentProgramId = hasPrograms ? programs[0].id : null;
    let currentLevel = (!hasPrograms && levels.length > 0) ? levels[0].level_number : 0;
    let currentModuleId = null;

    let completedSet = new Set(JSON.parse(localStorage.getItem('bbs_completed') || '[]'));
    let bookmarkedSet = new Set(JSON.parse(localStorage.getItem('bbs_bookmarked') || '[]'));
    let collapsedCourses = new Set();
    let collapsedChapters = new Set();

    function applyTheme(theme, showNotice = false) {
      currentTheme = theme;
      document.documentElement.classList.remove('dark', 'light');
      document.documentElement.classList.add(theme);
      localStorage.setItem('bbs_theme', theme);
      const icon = document.getElementById('theme-icon');
      if (icon) {
        icon.innerText = theme === 'dark' ? '🌙' : '☀️';
      }
      if (showNotice) {
        showToast(theme === 'dark' ? 'Night Mode Activated' : 'Day Mode Activated', theme === 'dark' ? '🌙' : '☀️');
      }
    }

    function toggleTheme() {
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme, true);
    }

    function renderMarkdown(md) {
      if (window.marked) {
        return marked.parse(md || '');
      }
      return (md || '').replace(/\n/g, '<br/>');
    }

    function init() {
      applyTheme(currentTheme, false);
      renderTabs();
      if (hasPrograms && programs.length > 0) {
        loadProgram(programs[0].id);
      } else if (levels.length > 0) {
        loadLevel(levels[0].level_number);
      }
      updateBadgeCounts();

      const searchInput = document.getElementById('search-input');
      if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
      }

      // Global keyboard navigation
      document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
          if (e.key === 'Escape') {
            e.target.blur();
            clearSearch();
          }
          return;
        }
        if (e.key === ']' || e.key === 'n' || e.key === 'N') goToNextModule();
        if (e.key === '[' || e.key === 'p' || e.key === 'P') goToPrevModule();
        if (e.key === 'm' || e.key === 'M') toggleComplete();
        if (e.key === 'b' || e.key === 'B') toggleBookmark();
        if (e.key === 'd' || e.key === 'D') toggleTheme();
        if (e.key === 't' || e.key === 'T') toggleTheaterMode();
        if (e.key === 'f' || e.key === 'F') toggleFocusMode();
        if (e.key === '/') {
          e.preventDefault();
          if (searchInput) searchInput.focus();
        }
        if (e.key === '?') toggleShortcutsModal();
        if (e.key === 'Escape') {
          const modal = document.getElementById('shortcuts-modal');
          if (modal && modal.classList.contains('open')) toggleShortcutsModal();
        }
      });
    }

    function showToast(msg, icon = '⚡') {
      const toast = document.getElementById('toast');
      const iconEl = document.getElementById('toast-icon');
      const msgEl = document.getElementById('toast-msg');
      if (!toast) return;

      iconEl.innerText = icon;
      msgEl.innerText = msg;
      toast.classList.add('show');
      clearTimeout(window._toastTimer);
      window._toastTimer = setTimeout(() => {
        toast.classList.remove('show');
      }, 2600);
    }

    function triggerConfetti() {
      const canvas = document.getElementById('confetti-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;

      const particles = [];
      const colors = ['#ff5a00', '#10b981', '#06b6d4', '#f59e0b', '#8b5cf6', '#ffffff'];
      for (let i = 0; i < 70; i++) {
        particles.push({
          x: canvas.width / 2,
          y: canvas.height / 2,
          r: Math.random() * 6 + 3,
          color: colors[Math.floor(Math.random() * colors.length)],
          vx: (Math.random() - 0.5) * 16,
          vy: (Math.random() - 0.7) * 16,
          gravity: 0.35,
          tilt: Math.random() * 10,
          tiltAngle: 0,
          tiltAngleInc: Math.random() * 0.1 + 0.05,
          alpha: 1
        });
      }

      let animId;
      function render() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;
        particles.forEach(p => {
          p.x += p.vx;
          p.y += p.vy;
          p.vy += p.gravity;
          p.alpha -= 0.015;
          p.tiltAngle += p.tiltAngleInc;
          p.tilt = Math.sin(p.tiltAngle) * 10;

          if (p.alpha > 0) {
            alive = true;
            ctx.globalAlpha = Math.max(0, p.alpha);
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.lineWidth = p.r;
            ctx.strokeStyle = p.color;
            ctx.moveTo(p.x + p.tilt + p.r / 2, p.y);
            ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 2);
            ctx.stroke();
          }
        });
        if (alive) {
          animId = requestAnimationFrame(render);
        } else {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          cancelAnimationFrame(animId);
        }
      }
      render();
    }

    function toggleFocusMode() {
      isFocusMode = !isFocusMode;
      const sidebar = document.getElementById('sidebar');
      const btn = document.getElementById('btn-focus-toggle');
      if (sidebar) sidebar.classList.toggle('focus-hidden', isFocusMode);
      if (btn) {
        btn.innerText = isFocusMode ? '⇹' : '⇸';
        btn.title = isFocusMode ? 'Exit Focus Mode (F)' : 'Focus Mode (F)';
      }
      showToast(isFocusMode ? 'Focus Mode ON' : 'Focus Mode OFF', '👁');
    }

    function toggleShortcutsModal() {
      const modal = document.getElementById('shortcuts-modal');
      if (modal) modal.classList.toggle('open');
    }

    function closeShortcutsModal(e) {
      if (e.target.id === 'shortcuts-modal') toggleShortcutsModal();
    }

    function setFilter(filterType) {
      activeFilter = filterType;
      ['all', 'ready', 'done', 'saved'].forEach(f => {
        const el = document.getElementById(`filter-${f}`);
        if (el) el.classList.toggle('active', filterType === f);
      });
      renderSidebar();
    }

    function updateBadgeCounts() {
      const totalCount = modules.length;
      const readyCount = modules.filter(m => m.video_url || m.notes).length;
      const doneCount = completedSet.size;
      const savedCount = bookmarkedSet.size;

      const elAll = document.getElementById('count-all');
      const elReady = document.getElementById('count-ready');
      const elDone = document.getElementById('count-done');
      const elSaved = document.getElementById('count-saved');
      
      if (elAll) elAll.innerText = totalCount;
      if (elReady) elReady.innerText = readyCount;
      if (elDone) elDone.innerText = doneCount;
      if (elSaved) elSaved.innerText = savedCount;

      const overallPct = Math.round((doneCount / totalCount) * 100) || 0;
      const pctEl = document.getElementById('overall-pct-text');
      if (pctEl) pctEl.innerText = `${overallPct}%`;
    }

    function openMobileSidebar() {
      document.getElementById('sidebar').classList.add('mobile-open');
      document.getElementById('mobile-backdrop').classList.add('active');
    }

    function closeMobileSidebar() {
      document.getElementById('sidebar').classList.remove('mobile-open');
      document.getElementById('mobile-backdrop').classList.remove('active');
    }

    function getModulesForCurrentTab() {
      if (hasPrograms) {
        const tabCourses = courses.filter(c => c.program_id === currentProgramId);
        const courseIds = new Set(tabCourses.map(c => c.id));
        return modules.filter(m => courseIds.has(m.course_id));
      } else {
        return modules.filter(m => m.level_number === currentLevel);
      }
    }

    function renderTabs() {
      const container = document.getElementById('level-tabs');
      if (!container) return;

      if (hasPrograms) {
        container.innerHTML = programs.map(p => {
          const pCourses = courses.filter(c => c.program_id === p.id);
          const pCourseIds = new Set(pCourses.map(c => c.id));
          const pMods = modules.filter(m => pCourseIds.has(m.course_id));
          const pDone = pMods.filter(m => completedSet.has(m.id)).length;
          const allDone = pMods.length > 0 && pDone === pMods.length;
          const isActive = p.id === currentProgramId;

          return `
            <button class="level-tab ${isActive ? 'active' : ''} ${allDone ? 'all-done' : ''}" 
                    onclick="loadProgram('${p.id}')" title="${p.title}">
              <span class="level-tab-dot"></span>
              <span>${p.code || p.title}</span>
              <span style="opacity:0.75;font-size:0.72rem;font-weight:normal;">${p.title}</span>
            </button>
          `;
        }).join('');
      } else {
        container.innerHTML = levels.map(lvl => {
          const lvlMods = modules.filter(m => m.level_number === lvl.level_number);
          const lvlDone = lvlMods.filter(m => completedSet.has(m.id)).length;
          const allDone = lvlMods.length > 0 && lvlDone === lvlMods.length;
          return `
            <button class="level-tab ${lvl.level_number === currentLevel ? 'active' : ''} ${allDone ? 'all-done' : ''}" 
                    onclick="loadLevel(${lvl.level_number})" title="Level ${lvl.level_number}: ${lvl.title || ''}">
              <span class="level-tab-dot"></span>
              <span>L${lvl.level_number}</span>
              <span>${lvl.title || 'Level ' + lvl.level_number}</span>
            </button>
          `;
        }).join('');
      }
    }

    function loadProgram(progId) {
      currentProgramId = progId;
      renderTabs();
      updateProgramMeta();
      renderSidebar();

      // Auto-select first available lesson in this program
      const tabMods = getModulesForCurrentTab();
      const firstReady = tabMods.find(m => m.video_url || m.notes) || tabMods[0];
      if (firstReady && (!currentModuleId || !tabMods.find(m => m.id === currentModuleId))) {
        selectModule(firstReady.id);
      }
    }

    function loadLevel(lvlNum) {
      currentLevel = lvlNum;
      renderTabs();
      updateProgramMeta();
      renderSidebar();
      
      const lvlMods = modules.filter(m => m.level_number === lvlNum);
      const firstReady = lvlMods.find(m => m.video_url || m.notes) || lvlMods[0];
      if (firstReady && (!currentModuleId || !modules.find(m => m.id === currentModuleId && m.level_number === lvlNum))) {
        selectModule(firstReady.id);
      }
    }

    function updateProgramMeta() {
      let title = 'Curriculum';
      let tabMods = [];

      if (hasPrograms) {
        const prog = programs.find(p => p.id === currentProgramId);
        title = prog ? `${prog.code || ''} · ${prog.title}` : 'Program';
        tabMods = getModulesForCurrentTab();
      } else {
        const lvl = levels.find(l => l.level_number === currentLevel);
        title = `Level ${currentLevel}: ${lvl ? (lvl.title || 'Curriculum') : ''}`;
        tabMods = modules.filter(m => m.level_number === currentLevel);
      }

      const doneCount = tabMods.filter(m => completedSet.has(m.id)).length;
      const pct = Math.round((doneCount / (tabMods.length || 1)) * 100) || 0;

      const titleEl = document.getElementById('level-active-title');
      const textEl = document.getElementById('level-prog-text');
      const fillEl = document.getElementById('level-prog-fill');

      if (titleEl) titleEl.innerText = title;
      if (textEl) textEl.innerText = `${doneCount}/${tabMods.length}`;
      if (fillEl) fillEl.style.width = `${pct}%`;
      updateBadgeCounts();
    }

    function toggleAllAccordions() {
      allAccordionsCollapsed = !allAccordionsCollapsed;
      const btn = document.getElementById('btn-toggle-accordions');
      if (btn) btn.innerText = allAccordionsCollapsed ? 'Expand All' : 'Collapse All';
      
      const tabCourses = hasPrograms ? courses.filter(c => c.program_id === currentProgramId) : courses.filter(c => c.level_number === currentLevel);
      tabCourses.forEach(c => {
        if (allAccordionsCollapsed) collapsedCourses.add(c.id);
        else collapsedCourses.delete(c.id);
      });
      chapters.forEach(ch => {
        if (allAccordionsCollapsed) collapsedChapters.add(ch.id);
        else collapsedChapters.delete(ch.id);
      });
      renderSidebar();
    }

    function toggleCourse(cId) {
      if (collapsedCourses.has(cId)) collapsedCourses.delete(cId);
      else collapsedCourses.add(cId);
      renderSidebar();
    }

    function toggleChapter(chId) {
      if (collapsedChapters.has(chId)) collapsedChapters.delete(chId);
      else collapsedChapters.add(chId);
      renderSidebar();
    }

    function renderSidebar() {
      const nav = document.getElementById('nav-list');
      if (!nav) return;

      const tabCourses = hasPrograms ? courses.filter(c => c.program_id === currentProgramId) : courses.filter(c => c.level_number === currentLevel);
      
      let html = '';
      tabCourses.forEach(c => {
        let cMods = modules.filter(m => m.course_id === c.id);
        
        if (activeFilter === 'ready') {
          cMods = cMods.filter(m => m.video_url || m.notes);
          if (cMods.length === 0) return;
        } else if (activeFilter === 'done') {
          cMods = cMods.filter(m => completedSet.has(m.id));
          if (cMods.length === 0) return;
        } else if (activeFilter === 'saved') {
          cMods = cMods.filter(m => bookmarkedSet.has(m.id));
          if (cMods.length === 0) return;
        }

        const isCourseCollapsed = collapsedCourses.has(c.id);
        const releaseDate = c.release_date ? new Date(c.release_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : null;

        html += `
          <div class="course-group ${isCourseCollapsed ? 'collapsed' : ''}">
            <div class="course-header" onclick="toggleCourse('${c.id}')">
              <div class="course-header-left">
                <span class="course-chevron">▼</span>
                <span>${c.title}</span>
              </div>
              ${releaseDate ? `<span class="course-release-tag">🗓 ${releaseDate}</span>` : ''}
            </div>
            <div class="course-body">
        `;

        const cChapters = chapters.filter(ch => ch.course_id === c.id);
        const cChapterIds = new Set(cChapters.map(ch => ch.id));
        const unassignedMods = cMods.filter(m => !m.chapter_id || !cChapterIds.has(m.chapter_id));

        // Render direct/unassigned modules first
        if (unassignedMods.length > 0) {
          unassignedMods.forEach(m => {
            html += renderModuleItem(m);
          });
        }

        // Render chapter modules
        cChapters.forEach(ch => {
          let chMods = modules.filter(m => m.chapter_id === ch.id);
          if (activeFilter === 'ready') chMods = chMods.filter(m => m.video_url || m.notes);
          else if (activeFilter === 'done') chMods = chMods.filter(m => completedSet.has(m.id));
          else if (activeFilter === 'saved') chMods = chMods.filter(m => bookmarkedSet.has(m.id));

          if (chMods.length === 0 && activeFilter !== 'all') return;

          const isCollapsed = collapsedChapters.has(ch.id);
          const chDone = chMods.filter(m => completedSet.has(m.id)).length;

          html += `
            <div class="chapter-group ${isCollapsed ? 'collapsed' : ''}">
              <div class="chapter-header" onclick="toggleChapter('${ch.id}')">
                <div class="chapter-title-text">
                  <span class="chapter-chevron">▼</span>
                  <span>${ch.title}</span>
                </div>
                <span class="chapter-count">${chDone}/${chMods.length}</span>
              </div>
              <div class="chapter-lessons">
                ${chMods.map(m => renderModuleItem(m)).join('')}
              </div>
            </div>
          `;
        });

        html += `</div></div>`;
      });

      nav.innerHTML = html || `<div style="text-align:center;padding:36px 14px;color:var(--text-tertiary);font-size:0.84rem;">No lessons found matching this filter in this program.</div>`;
    }

    function renderModuleItem(m) {
      const isDone = completedSet.has(m.id);
      const isSaved = bookmarkedSet.has(m.id);
      const isActive = m.id === currentModuleId;
      const isReady = Boolean(m.video_url || m.notes);

      let badge = '';
      if (m.video_url) {
        badge = `<span class="lesson-badge-pill pill-video">🎥 Video</span>`;
      } else if (m.notes) {
        badge = `<span class="lesson-badge-pill pill-notes">📝 Notes</span>`;
      } else {
        badge = `<span class="lesson-badge-pill pill-upcoming">⏳ Outline</span>`;
      }

      return `
        <div class="lesson-item ${isActive ? 'active' : ''} ${isDone ? 'completed' : ''} ${!isReady ? 'upcoming' : ''}" 
             onclick="selectModule('${m.id}')" id="mod-item-${m.id}">
          <div class="lesson-left">
            <span class="lesson-icon">${m.video_url ? '🎥' : (m.notes ? '📝' : '📄')}</span>
            <span class="lesson-title-text">${m.title || 'Untitled'}</span>
          </div>
          <div class="lesson-right-badges">
            ${isSaved ? '<span class="lesson-bookmark-icon">★</span>' : ''}
            ${badge}
            ${m.duration_minutes ? `<span class="lesson-duration" style="font-size:0.65rem;font-family:'JetBrains Mono',monospace;color:var(--text-tertiary);margin-left:4px;">${m.duration_minutes}m</span>` : ''}
          </div>
        </div>
      `;
    }

    function parseVideoInfo(videoUrl) {
      if (!videoUrl) return null;
      const match = videoUrl.match(/(?:iframe\.mediadelivery\.net\/(?:embed|play)|player\.mediadelivery\.net\/play)\/(\d+)\/([\w-]+)/i) ||
                    videoUrl.match(/([0-9]{5,8})\/([a-f0-9-]{36})/i);
      if (match) {
        return {
          libraryId: match[1],
          videoId: match[2],
          embedUrl: `https://iframe.mediadelivery.net/embed/${match[1]}/${match[2]}`
        };
      }
      const rawUuid = videoUrl.match(/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i);
      if (rawUuid) {
        return {
          libraryId: '753332',
          videoId: rawUuid[1],
          embedUrl: `https://iframe.mediadelivery.net/embed/753332/${rawUuid[1]}`
        };
      }
      return null;
    }

    function selectModule(modId) {
      if (activeHls) {
        activeHls.destroy();
        activeHls = null;
      }

      currentModuleId = modId;
      const mod = modules.find(m => m.id === modId);
      if (!mod) return;

      const crs = courses.find(c => c.id === mod.course_id);
      const chp = chapters.find(ch => ch.id === mod.chapter_id);
      const prog = crs ? programs.find(p => p.id === crs.program_id) : null;

      // Ensure proper tab is active if selected via search or direct jump
      if (prog && prog.id !== currentProgramId) {
        currentProgramId = prog.id;
        renderTabs();
      }

      // Auto ensure its course and chapter are expanded
      if (mod.chapter_id) collapsedChapters.delete(mod.chapter_id);
      if (mod.course_id) collapsedCourses.delete(mod.course_id);

      renderSidebar();
      updateCompleteButton();
      updateBookmarkButton();
      updateProgramMeta();

      // Smooth scroll active lesson into view
      setTimeout(() => {
        const itemEl = document.getElementById(`mod-item-${modId}`);
        if (itemEl) itemEl.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }, 50);

      if (window.innerWidth <= 960) {
        closeMobileSidebar();
      }

      const breadcrumbEl = document.getElementById('breadcrumb');
      if (breadcrumbEl) {
        breadcrumbEl.innerHTML = `
          <span class="breadcrumb-item">${prog ? (prog.code || prog.title) : 'L' + mod.level_number}</span>
          <span class="breadcrumb-sep">&rsaquo;</span>
          <span class="breadcrumb-item">${crs ? crs.title : ''}</span>
          ${chp ? `<span class="breadcrumb-sep">&rsaquo;</span><span class="breadcrumb-item">${chp.title}</span>` : ''}
          <span class="breadcrumb-sep">&rsaquo;</span>
          <span class="breadcrumb-current">${mod.title}</span>
        `;
      }

      const isReady = Boolean(mod.video_url || m_hasNotes(mod));
      const videoInfo = parseVideoInfo(mod.video_url);

      let bodyHtml = `
        <div class="lesson-hero">
          <div class="lesson-hero-header-row">
            <h1 class="lesson-hero-title">${mod.title}</h1>
          </div>
          <div class="hero-tags">
            <span class="hero-tag tag-level">${prog ? prog.title : 'LEVEL ' + mod.level_number}</span>
            ${crs ? `<span class="hero-tag tag-duration">📚 ${crs.title}</span>` : ''}
            ${mod.duration_minutes ? `<span class="hero-tag tag-duration">⏱ ${mod.duration_minutes} MINS</span>` : ''}
            ${mod.video_url ? '<span class="hero-tag tag-video-live">⚡ BUNNY HD STREAM</span>' : ''}
            ${mod.notes ? '<span class="hero-tag tag-notes-live">📝 STUDY NOTES</span>' : ''}
            ${!isReady ? '<span class="hero-tag tag-upcoming">⏳ UPCOMING RELEASE</span>' : ''}
            ${mod.is_required ? '<span class="hero-tag tag-req">⭐ REQUIRED</span>' : ''}
          </div>
        </div>
      `;

      // If lesson is upcoming / empty
      if (!isReady) {
        const releaseDate = crs && crs.release_date ? new Date(crs.release_date).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' }) : 'Scheduled Soon';
        const nextReady = modules.find((m, i) => i > modules.findIndex(x => x.id === modId) && (m.video_url || m.notes));

        bodyHtml += `
          <div class="upcoming-card">
            <div class="upcoming-icon">🚀</div>
            <div class="upcoming-title">Lesson In Production</div>
            <div class="upcoming-desc">
              <strong>${mod.title}</strong> is an officially registered topic under <strong>${crs ? crs.title : 'Coach Adib Curriculum'}</strong>.<br/>
              The syllabus has been mapped, and lessons are being published according to the release schedule (Target: <em>${releaseDate}</em>).
            </div>
            <div class="upcoming-actions">
              ${nextReady ? `
                <button class="btn btn-primary" onclick="selectModule('${nextReady.id}')">
                  👉 Jump to Next Available Lesson (${nextReady.title})
                </button>
              ` : `
                <button class="btn btn-primary" onclick="loadProgram('${programs[0].id}')">
                  👉 Jump to Overview
                </button>
              `}
              <button class="btn btn-secondary" onclick="setFilter('ready')">
                🔍 Filter Ready Lessons Only
              </button>
            </div>
          </div>
        `;
      }

      // Video Player Section
      if (videoInfo) {
        bodyHtml += `
          <div class="video-hero-card ${isTheater ? 'theater-mode' : ''}" id="video-card">
            <div class="video-card-topbar">
              <div class="video-stream-badge">
                <span class="stream-dot"></span>
                <span id="player-mode-badge">${playerMode === 'iframe' ? 'Bunny Embed Player' : 'Bunny CDN Direct Stream'}</span>
              </div>
              <div class="video-controls-quick">
                <button class="jump-btn" onclick="jumpVideo(-10)" title="Rewind 10s">↺ 10s</button>
                <button class="jump-btn" onclick="jumpVideo(10)" title="Forward 10s">10s ↻</button>
                <button class="speed-btn ${currentSpeed === 1 ? 'active' : ''}" onclick="setSpeed(1)">1x</button>
                <button class="speed-btn ${currentSpeed === 1.25 ? 'active' : ''}" onclick="setSpeed(1.25)">1.25x</button>
                <button class="speed-btn ${currentSpeed === 1.5 ? 'active' : ''}" onclick="setSpeed(1.5)">1.5x</button>
                <button class="speed-btn ${currentSpeed === 2 ? 'active' : ''}" onclick="setSpeed(2)">2x</button>
                <button class="player-toggle-btn" id="btn-toggle-player" onclick="togglePlayerMode('${mod.id}')" title="Switch player mode">
                  ${playerMode === 'iframe' ? '⇄ Use HLS' : '⇄ Use Embed'}
                </button>
              </div>
            </div>
            <div class="video-wrapper" id="video-wrapper"></div>
          </div>
        `;
      }

      // Description & Study Notes Section
      if (mod.description || mod.notes) {
        bodyHtml += `
          <div class="study-card">
            <div class="study-header">
              <div class="study-title">
                <span>📖 Lesson Notes & Summary</span>
              </div>
              <button class="btn btn-secondary" onclick="copyAllNotes()" style="font-size:0.75rem;padding:4px 10px;">
                📋 Copy Notes
              </button>
            </div>
            ${mod.description ? `<div style="margin-bottom:16px;color:var(--text-secondary);font-size:0.92rem;">${renderMarkdown(mod.description)}</div>` : ''}
            <div class="markdown-body" id="markdown-notes-body">
              ${renderMarkdown(mod.notes)}
            </div>
          </div>
        `;
      }

      // Quizzes Section
      if (mod.quiz && Array.isArray(mod.quiz) && mod.quiz.length > 0) {
        bodyHtml += `
          <div class="study-card">
            <div class="study-header">
              <div class="study-title">
                <span>🎯 Practice & Knowledge Check (${mod.quiz.length} Questions)</span>
              </div>
            </div>
            <div class="quiz-section">
        `;
        mod.quiz.forEach((q, qIdx) => {
          bodyHtml += `
            <div class="quiz-item-card">
              <div class="quiz-question-title">${qIdx + 1}. ${q.question}</div>
              <div class="quiz-options-list">
                ${(q.options || []).map((opt, optIdx) => `
                  <button class="quiz-opt-btn" onclick="checkAnswer(this, ${optIdx}, ${q.correct_answer || 0}, '${escapeQuotes(q.explanation)}')">
                    <span>${String.fromCharCode(65 + optIdx)}.</span>
                    <span>${opt}</span>
                  </button>
                `).join('')}
              </div>
              <div class="quiz-feedback-box"></div>
            </div>
          `;
        });
        bodyHtml += `</div></div>`;
      }

      // Footer Navigation Controls
      const idx = modules.findIndex(m => m.id === modId);
      const prevMod = idx > 0 ? modules[idx - 1] : null;
      const nextMod = idx < modules.length - 1 ? modules[idx + 1] : null;

      bodyHtml += `
        <div class="lesson-footer-nav">
          ${prevMod ? `
            <button class="btn btn-secondary" onclick="goToPrevModule()">
              ← Previous (${prevMod.title})
            </button>
          ` : `<div></div>`}
          ${nextMod ? `
            <button class="btn btn-primary" onclick="goToNextModule()">
              Next Lesson (${nextMod.title}) →
            </button>
          ` : `<div></div>`}
        </div>
      `;

      document.getElementById('content-container').innerHTML = bodyHtml;
      document.getElementById('main-content').scrollTop = 0;

      // Initialize video
      if (videoInfo) {
        setupVideoPlayer(videoInfo);
      }
    }

    function m_hasNotes(mod) {
      return Boolean(mod.notes && mod.notes.trim().length > 0);
    }

    function togglePlayerMode(modId) {
      playerMode = playerMode === 'hls' ? 'iframe' : 'hls';
      localStorage.setItem('bbs_player_mode', playerMode);
      const btn = document.getElementById('btn-toggle-player');
      if (btn) btn.innerText = playerMode === 'iframe' ? '⇄ Use HLS' : '⇄ Use Embed';
      const badge = document.getElementById('player-mode-badge');
      if (badge) badge.innerText = playerMode === 'iframe' ? 'Bunny Embed Player' : 'Bunny CDN Direct Stream';
      const mod = modules.find(m => m.id === modId);
      if (mod) {
        const vInfo = parseVideoInfo(mod.video_url);
        if (vInfo) setupVideoPlayer(vInfo);
      }
      showToast(playerMode === 'iframe' ? 'Switched to Embed Player' : 'Switched to Native HLS Stream', '⚡');
    }

    function setupVideoPlayer(videoInfo) {
      const wrapper = document.getElementById('video-wrapper');
      if (!wrapper || !videoInfo) return;

      if (activeHls) {
        activeHls.destroy();
        activeHls = null;
      }

      if (playerMode === 'iframe' || videoInfo.libraryId !== '753332') {
        wrapper.innerHTML = `
          <iframe 
            src="${videoInfo.embedUrl}?autoplay=true&preload=true&responsive=true" 
            loading="lazy" 
            style="border:0;position:absolute;top:0;left:0;width:100%;height:100%;" 
            allow="accelerometer;gyroscope;autoplay;encrypted-media;picture-in-picture;" 
            allowfullscreen="true">
          </iframe>
        `;
        return;
      }

      // HLS mode for library 753332
      wrapper.innerHTML = `
        <video id="bbs-video-player" controls playsinline preload="metadata" poster="https://vz-b7e89a3b-a06.b-cdn.net/${videoInfo.videoId}/thumbnail.jpg"></video>
      `;

      const video = document.getElementById('bbs-video-player');
      if (!video) return;

      const cdnUrl = `https://vz-b7e89a3b-a06.b-cdn.net/${videoInfo.videoId}/playlist.m3u8`;
      const streamUrl = cdnUrl;

      if (Hls.isSupported()) {
        const hls = new Hls({
          maxBufferLength: 30,
          maxMaxBufferLength: 60,
          enableWorker: true
        });

        let hasFallenBack = false;
        hls.on(Hls.Events.ERROR, function(event, data) {
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                if (!hasFallenBack && (location.hostname === '127.0.0.1' || location.hostname === 'localhost')) {
                  hasFallenBack = true;
                  console.warn('Network error on direct CDN stream, attempting local video-proxy...');
                  hls.loadSource(`/video-proxy/${videoInfo.videoId}/playlist.m3u8`);
                  hls.startLoad();
                } else if (!hasFallenBack) {
                  hasFallenBack = true;
                  console.warn('Direct HLS blocked, falling back to embed player...');
                  playerMode = 'iframe';
                  setupVideoPlayer(videoInfo);
                }
                break;
              default:
                hls.destroy();
                playerMode = 'iframe';
                setupVideoPlayer(videoInfo);
                break;
            }
          }
        });

        hls.loadSource(streamUrl);
        hls.attachMedia(video);
        activeHls = hls;
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = streamUrl;
        video.onerror = () => {
          playerMode = 'iframe';
          setupVideoPlayer(videoInfo);
        };
      }

      video.playbackRate = currentSpeed;
      video.addEventListener('ended', () => {
        if (currentModuleId && !completedSet.has(currentModuleId)) {
          toggleComplete();
        }
      });
    }

    function jumpVideo(sec) {
      const video = document.getElementById('bbs-video-player');
      if (video) video.currentTime = Math.max(0, video.currentTime + sec);
    }

    function setSpeed(spd) {
      currentSpeed = spd;
      const video = document.getElementById('bbs-video-player');
      if (video) video.playbackRate = spd;
      document.querySelectorAll('.speed-btn').forEach(b => {
        b.classList.toggle('active', b.innerText === spd + 'x');
      });
      showToast(`Playback Speed: ${spd}x`, '⚡');
    }

    function toggleTheaterMode() {
      isTheater = !isTheater;
      const card = document.getElementById('video-card');
      if (card) {
        card.classList.toggle('theater-mode', isTheater);
      }
    }

    function copyAllNotes() {
      const mod = modules.find(m => m.id === currentModuleId);
      if (!mod || !mod.notes) return;
      navigator.clipboard.writeText(mod.notes).then(() => {
        showToast('All notes copied to clipboard!', '📋');
      });
    }

    function escapeQuotes(str) {
      return (str || '')
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '&quot;')
        .replace(/\n/g, ' ');
    }

    function checkAnswer(el, chosen, correct, explain) {
      const parent = el.closest('.quiz-item-card');
      const allOpts = parent.querySelectorAll('.quiz-opt-btn');
      allOpts.forEach(o => o.classList.remove('correct', 'wrong'));

      if (chosen === correct) {
        el.classList.add('correct');
        showToast('Correct answer!', '✨');
      } else {
        el.classList.add('wrong');
        allOpts[correct].classList.add('correct');
      }

      const explainEl = parent.querySelector('.quiz-feedback-box');
      if (explainEl) {
        explainEl.innerHTML = '<strong>💡 Key Insight:</strong> ' + (explain || (chosen === correct ? 'Correct!' : 'Review this concept again.'));
        explainEl.style.display = 'block';
      }
    }

    function toggleComplete() {
      if (!currentModuleId) return;
      if (completedSet.has(currentModuleId)) {
        completedSet.delete(currentModuleId);
        showToast('Marked as incomplete', '○');
      } else {
        completedSet.add(currentModuleId);
        triggerConfetti();
        showToast('Lesson Completed! Great work!', '🎉');
      }
      localStorage.setItem('bbs_completed', JSON.stringify([...completedSet]));
      updateCompleteButton();
      renderSidebar();
      updateProgramMeta();
    }

    function toggleBookmark() {
      if (!currentModuleId) return;
      if (bookmarkedSet.has(currentModuleId)) {
        bookmarkedSet.delete(currentModuleId);
        showToast('Bookmark removed', '☆');
      } else {
        bookmarkedSet.add(currentModuleId);
        showToast('Lesson bookmarked for quick review!', '★');
      }
      localStorage.setItem('bbs_bookmarked', JSON.stringify([...bookmarkedSet]));
      updateBookmarkButton();
      renderSidebar();
      updateBadgeCounts();
    }

    function updateCompleteButton() {
      const btn = document.getElementById('btn-complete-action');
      if (!currentModuleId || !btn) return;
      if (completedSet.has(currentModuleId)) {
        btn.innerHTML = '<span>✓</span> <span class="btn-done-text btn-text-hide">Done</span>';
        btn.classList.add('btn-done');
        btn.classList.remove('btn-primary');
      } else {
        btn.innerHTML = '<span>✓</span> <span class="btn-done-text btn-text-hide">Mark Done</span>';
        btn.classList.remove('btn-done');
        btn.classList.add('btn-primary');
      }
    }

    function updateBookmarkButton() {
      const btn = document.getElementById('btn-bookmark-action');
      if (!currentModuleId || !btn) return;
      const isSaved = bookmarkedSet.has(currentModuleId);
      btn.classList.toggle('btn-bookmarked', isSaved);
      btn.innerHTML = `<span>${isSaved ? '★' : '☆'}</span> <span class="btn-text-hide">${isSaved ? 'Saved' : 'Save'}</span>`;
    }

    function goToNextModule() {
      if (!currentModuleId) return;
      const idx = modules.findIndex(m => m.id === currentModuleId);
      if (idx < modules.length - 1) {
        const next = modules[idx + 1];
        selectModule(next.id);
      }
    }

    function goToPrevModule() {
      if (!currentModuleId) return;
      const idx = modules.findIndex(m => m.id === currentModuleId);
      if (idx > 0) {
        const prev = modules[idx - 1];
        selectModule(prev.id);
      }
    }

    function handleSearch(e) {
      const query = e.target.value.toLowerCase().trim();
      const clearBtn = document.getElementById('search-clear-btn');
      if (clearBtn) clearBtn.style.display = query ? 'block' : 'none';

      if (!query) {
        renderSidebar();
        return;
      }
      const matched = modules.filter(m => 
        (m.title && m.title.toLowerCase().includes(query)) || 
        (m.notes && m.notes.toLowerCase().includes(query)) ||
        (m.description && m.description.toLowerCase().includes(query))
      );
      const nav = document.getElementById('nav-list');
      if (nav) {
        nav.innerHTML = `
          <div class="course-header" style="color: var(--accent-emerald);">Results (${matched.length})</div>
          ${matched.map(m => renderModuleItem(m)).join('')}
        `;
      }
    }

    function clearSearch() {
      const input = document.getElementById('search-input');
      if (input) input.value = '';
      const clearBtn = document.getElementById('search-clear-btn');
      if (clearBtn) clearBtn.style.display = 'none';
      renderSidebar();
    }

    init();
  </script>
</body>
</html>
"""
    with open("offline_site/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✓ Successfully generated Coach Adib offline site with 4 programs & 408 lessons!")

if __name__ == "__main__":
    build_offline_site()
