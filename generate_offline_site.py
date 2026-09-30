#!/usr/bin/env python3
"""
Generate a fully responsive, dynamic, mobile-adaptable and desktop-suitable web application
for Blueprint Business Service (Levels 0-5).
Includes content readiness badges, upcoming release cards, and auto-jump to active lessons.
"""
import json
import os

def build_offline_site():
    os.makedirs("offline_site", exist_ok=True)
    with open("bbs_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    levels = sorted(data.get("Level", []), key=lambda x: x.get("level_number", 0))
    courses = sorted(data.get("Course", []), key=lambda x: (x.get("level_number", 0), x.get("order", 0)))
    chapters = sorted(data.get("Chapter", []), key=lambda x: x.get("order", 0))
    modules = sorted(data.get("Module", []), key=lambda x: (x.get("level_number", 0), x.get("order", 0)))

    # Save data.js
    with open("offline_site/data.js", "w", encoding="utf-8") as f:
        f.write("window.BBS_DATA = " + json.dumps({
            "levels": levels,
            "courses": courses,
            "chapters": chapters,
            "modules": modules
        }, ensure_ascii=False) + ";\n")

    html_content = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=1.0, user-scalable=no">
  <title>BBS · Blueprint Business Service</title>
  <script src="marked.min.js"></script>
  <script src="hls.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #090d16;
      --bg-surface: #0f172a;
      --bg-card: #162036;
      --bg-card-hover: #1c2a47;
      --bg-elevated: #1e293b;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 90, 0, 0.5);
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-tertiary: #64748b;
      --accent-brand: #ff5a00;
      --accent-brand-hover: #ff6f22;
      --accent-brand-glow: rgba(255, 90, 0, 0.25);
      --accent-emerald: #10b981;
      --accent-rose: #f43f5e;
      --accent-amber: #f59e0b;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --sidebar-width: 370px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    html, body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg-base);
      color: var(--text-primary);
      height: 100%;
      width: 100%;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.14); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.28); }

    /* App Shell */
    #app-shell {
      display: flex;
      height: 100vh;
      height: 100dvh;
      width: 100vw;
      overflow: hidden;
      position: relative;
    }

    /* Sidebar / Mobile Drawer */
    #sidebar {
      width: var(--sidebar-width);
      background: var(--bg-surface);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      height: 100%;
      z-index: 50;
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Mobile Backdrop Overlay */
    #mobile-backdrop {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      z-index: 40;
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    #mobile-backdrop.active { display: block; opacity: 1; }

    /* Sidebar Header */
    .sidebar-header {
      padding: 14px 18px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(15, 23, 42, 0.95);
      flex-shrink: 0;
    }
    .brand-group { display: flex; align-items: center; gap: 10px; }
    .brand-logo {
      width: 32px;
      height: 32px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, #ff5a00, #ff8c42);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.85rem;
      color: white;
      box-shadow: 0 4px 12px var(--accent-brand-glow);
    }
    .brand-info h2 { font-size: 0.92rem; font-weight: 700; color: #fff; }
    .brand-info p { font-size: 0.7rem; color: var(--text-tertiary); }
    
    .btn-close-sidebar {
      display: none;
      background: rgba(255,255,255,0.06);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      width: 32px;
      height: 32px;
      border-radius: var(--radius-sm);
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1.1rem;
    }

    /* Level Tabs Bar */
    .level-tabs-container {
      overflow-x: auto;
      background: rgba(9, 13, 22, 0.75);
      border-bottom: 1px solid var(--border-subtle);
      flex-shrink: 0;
      -webkit-overflow-scrolling: touch;
    }
    .level-tabs {
      display: flex;
      padding: 8px 12px;
      gap: 6px;
      width: max-content;
    }
    .level-tab {
      padding: 6px 12px;
      border-radius: var(--radius-md);
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-secondary);
      cursor: pointer;
      font-size: 0.76rem;
      font-weight: 600;
      white-space: nowrap;
      transition: all 0.18s ease;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .level-tab:hover { background: rgba(255,255,255,0.04); color: #fff; }
    .level-tab.active {
      background: linear-gradient(135deg, rgba(255,90,0,0.18), rgba(255,90,0,0.06));
      color: #ff9d66;
      border-color: rgba(255,90,0,0.35);
      box-shadow: 0 2px 10px rgba(255,90,0,0.12);
    }

    /* Search & Filter Section */
    .search-section { padding: 10px 14px; border-bottom: 1px solid var(--border-subtle); flex-shrink: 0; }
    .search-input-wrap { position: relative; display: flex; align-items: center; margin-bottom: 8px; }
    .search-icon { position: absolute; left: 10px; width: 14px; height: 14px; color: var(--text-tertiary); }
    .search-input {
      width: 100%;
      padding: 8px 10px 8px 32px;
      background: rgba(9, 13, 22, 0.8);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      color: #fff;
      font-size: 0.82rem;
      outline: none;
      transition: all 0.2s;
    }
    .search-input:focus { border-color: var(--accent-brand); background: rgba(15, 23, 42, 0.9); }
    
    .filter-pills { display: flex; gap: 6px; }
    .filter-pill {
      padding: 3px 8px;
      border-radius: var(--radius-sm);
      font-size: 0.7rem;
      font-weight: 600;
      border: 1px solid var(--border-subtle);
      background: rgba(255,255,255,0.03);
      color: var(--text-tertiary);
      cursor: pointer;
      transition: all 0.15s;
    }
    .filter-pill:hover, .filter-pill.active {
      background: rgba(255,90,0,0.15);
      border-color: rgba(255,90,0,0.4);
      color: #ff9d66;
    }

    /* Level Progress Banner */
    .level-meta-bar {
      padding: 8px 14px;
      background: rgba(255,255,255,0.02);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.75rem;
      flex-shrink: 0;
    }
    .level-title-display { font-weight: 700; color: #fff; }
    .level-prog-wrap { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; color: var(--text-secondary); }
    .prog-bar-mini { width: 50px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 999px; overflow: hidden; }
    .prog-bar-fill { height: 100%; background: var(--accent-emerald); transition: width 0.3s ease; }

    /* Navigation List */
    .nav-list { flex: 1; overflow-y: auto; padding: 10px; -webkit-overflow-scrolling: touch; }
    
    .course-group { margin-bottom: 12px; }
    .course-header {
      font-size: 0.72rem;
      text-transform: uppercase;
      color: var(--accent-brand);
      font-weight: 800;
      letter-spacing: 0.06em;
      padding: 6px 8px;
      user-select: none;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .course-release-tag { font-size: 0.65rem; color: var(--text-tertiary); font-weight: 600; text-transform: none; }

    .chapter-group { margin-bottom: 6px; }
    .chapter-header {
      font-size: 0.8rem;
      font-weight: 700;
      color: #e2e8f0;
      padding: 8px 10px;
      border-radius: var(--radius-md);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: background 0.15s;
      min-height: 40px;
    }
    .chapter-header:hover { background: rgba(255,255,255,0.04); }
    .chapter-title-text { display: flex; align-items: center; gap: 6px; }
    .chapter-chevron { font-size: 0.65rem; color: var(--text-tertiary); transition: transform 0.2s ease; }
    .chapter-group.collapsed .chapter-chevron { transform: rotate(-90deg); }
    .chapter-group.collapsed .chapter-lessons { display: none; }
    .chapter-count { font-size: 0.68rem; color: var(--text-tertiary); font-weight: 500; }

    .chapter-lessons { padding-left: 4px; margin-top: 2px; }
    .lesson-item {
      padding: 9px 10px;
      border-radius: var(--radius-md);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2px;
      font-size: 0.82rem;
      color: var(--text-secondary);
      transition: all 0.15s ease;
      border-left: 3px solid transparent;
      min-height: 42px;
    }
    .lesson-item:hover { background: rgba(255, 255, 255, 0.05); color: #fff; }
    .lesson-item.active {
      background: var(--bg-card);
      color: #fff;
      font-weight: 600;
      border-left-color: var(--accent-brand);
    }
    .lesson-item.upcoming { opacity: 0.65; }
    .lesson-left { display: flex; align-items: center; gap: 8px; overflow: hidden; }
    .lesson-icon { font-size: 0.8rem; flex-shrink: 0; }
    .lesson-title-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .lesson-item.completed .lesson-left::before {
      content: "";
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--accent-emerald);
      flex-shrink: 0;
    }
    .lesson-badge-pill {
      font-size: 0.65rem;
      padding: 1px 5px;
      border-radius: 3px;
      font-weight: 700;
      margin-left: 6px;
      white-space: nowrap;
    }
    .pill-video { background: rgba(255,90,0,0.15); color: #ff8a4c; }
    .pill-notes { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
    .pill-upcoming { background: rgba(255,255,255,0.06); color: var(--text-tertiary); }

    /* Main Content Area */
    #main-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow-y: auto;
      background: var(--bg-base);
      position: relative;
      -webkit-overflow-scrolling: touch;
    }

    /* Top Sticky Bar */
    .topbar {
      padding: 12px 24px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(9, 13, 22, 0.88);
      backdrop-filter: blur(18px);
      position: sticky;
      top: 0;
      z-index: 25;
      flex-shrink: 0;
    }
    .topbar-left { display: flex; align-items: center; gap: 12px; overflow: hidden; }
    .btn-hamburger {
      display: none;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: #fff;
      width: 36px;
      height: 36px;
      border-radius: var(--radius-md);
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1.1rem;
      flex-shrink: 0;
    }
    .breadcrumb-nav {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.82rem;
      color: var(--text-tertiary);
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .breadcrumb-item { color: var(--text-secondary); font-weight: 500; }
    .breadcrumb-current { color: #fff; font-weight: 700; overflow: hidden; text-overflow: ellipsis; }
    .breadcrumb-sep { color: rgba(255,255,255,0.2); }

    .topbar-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
    .btn {
      padding: 8px 14px;
      border-radius: var(--radius-md);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
      border: 1px solid transparent;
      outline: none;
      min-height: 36px;
    }
    .btn-secondary { background: var(--bg-card); border-color: var(--border-subtle); color: var(--text-secondary); }
    .btn-secondary:hover { background: var(--bg-card-hover); color: #fff; }
    .btn-primary { background: linear-gradient(135deg, #ff5a00, #ff7e33); color: white; box-shadow: 0 4px 14px var(--accent-brand-glow); }
    .btn-done { background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.35); color: #34d399; }

    /* Content Layout Container */
    .content-container {
      max-width: 960px;
      margin: 0 auto;
      width: 100%;
      padding: 24px 28px 80px 28px;
    }

    /* Lesson Hero */
    .lesson-hero { margin-bottom: 22px; }
    .lesson-hero-title {
      font-size: 1.8rem;
      font-weight: 800;
      color: #fff;
      letter-spacing: -0.02em;
      line-height: 1.3;
      margin-bottom: 10px;
    }
    .hero-tags { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
    .hero-tag {
      padding: 3px 8px;
      border-radius: var(--radius-sm);
      font-size: 0.72rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .tag-duration { background: rgba(255,255,255,0.06); color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; }
    .tag-video-live { background: rgba(255,90,0,0.15); color: #ff8c4a; border: 1px solid rgba(255,90,0,0.3); }
    .tag-notes-live { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .tag-upcoming { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }

    /* Upcoming Release Hero Card */
    .upcoming-card {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(15, 23, 42, 0.9));
      border: 1px solid rgba(245, 158, 11, 0.25);
      border-radius: var(--radius-lg);
      padding: 32px 30px;
      margin-bottom: 28px;
      text-align: center;
    }
    .upcoming-icon { font-size: 2.5rem; margin-bottom: 12px; }
    .upcoming-title { font-size: 1.3rem; font-weight: 800; color: #fff; margin-bottom: 8px; }
    .upcoming-desc { font-size: 0.9rem; color: #cbd5e1; max-width: 580px; margin: 0 auto 20px auto; line-height: 1.6; }
    .upcoming-actions { display: flex; justify-content: center; gap: 12px; }

    /* Video Player */
    .video-hero-card {
      background: #000;
      border-radius: var(--radius-lg);
      overflow: hidden;
      border: 1px solid var(--border-subtle);
      margin-bottom: 28px;
      box-shadow: 0 16px 36px -12px rgba(0,0,0,0.8);
    }
    .video-hero-card.theater-mode {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 1000;
      border-radius: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
    }
    .video-card-topbar {
      padding: 8px 14px;
      background: #070a12;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.78rem;
    }
    .video-stream-badge { display: flex; align-items: center; gap: 6px; color: #cbd5e1; font-weight: 600; font-size: 0.75rem; }
    .stream-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-emerald); box-shadow: 0 0 6px var(--accent-emerald); }
    .video-controls-quick { display: flex; gap: 6px; align-items: center; }
    .speed-btn, .theater-btn {
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 700;
      background: rgba(255,255,255,0.06);
      color: var(--text-secondary);
      border: 1px solid var(--border-subtle);
      cursor: pointer;
    }
    .speed-btn.active { background: var(--accent-brand); color: white; border-color: var(--accent-brand); }
    .video-wrapper { position: relative; padding-bottom: 56.25%; height: 0; width: 100%; background: #000; }
    .video-hero-card.theater-mode .video-wrapper { flex: 1; height: 100%; padding-bottom: 0; }
    .video-wrapper video { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; outline: none; }

    /* Notes Section */
    .notes-section {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 28px 30px;
      margin-bottom: 28px;
    }
    .notes-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border-subtle);
    }
    .notes-title { font-size: 1.05rem; font-weight: 700; color: #fff; }

    /* Markdown Body */
    .markdown-body { line-height: 1.75; font-size: 0.94rem; color: #cbd5e1; word-break: break-word; }
    .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 { color: #fff; margin: 26px 0 12px 0; font-weight: 800; }
    .markdown-body h2 { font-size: 1.3rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px; }
    .markdown-body h3 { font-size: 1.1rem; }
    .markdown-body p { margin-bottom: 14px; }
    .markdown-body ul, .markdown-body ol { margin-left: 20px; margin-bottom: 18px; }
    .markdown-body li { margin-bottom: 5px; }
    .markdown-body blockquote {
      border-left: 4px solid var(--accent-brand);
      padding: 12px 16px;
      margin: 16px 0;
      color: #f1f5f9;
      background: linear-gradient(90deg, rgba(255,90,0,0.08), rgba(255,90,0,0.01));
      border-radius: 0 var(--radius-md) var(--radius-md) 0;
    }
    .markdown-body table { width: 100%; display: block; overflow-x: auto; border-collapse: collapse; margin: 20px 0; }
    .markdown-body th, .markdown-body td { border: 1px solid var(--border-subtle); padding: 10px 14px; text-align: left; }
    .markdown-body th { background: rgba(9, 13, 22, 0.7); color: #fff; font-weight: 700; }
    .markdown-body code {
      font-family: 'JetBrains Mono', monospace;
      background: rgba(9, 13, 22, 0.9);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.84em;
      color: #fb7185;
      border: 1px solid var(--border-subtle);
    }
    .markdown-body pre { background: #090d16; border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 14px; margin: 16px 0; overflow-x: auto; }
    .markdown-body pre code { background: transparent; padding: 0; border: none; color: #e2e8f0; }

    /* Quiz Section */
    .quiz-section {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 28px 30px;
      margin-bottom: 28px;
    }
    .quiz-main-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border-subtle);
    }
    .quiz-headline { font-size: 1.05rem; font-weight: 700; color: #fff; }
    .quiz-score-badge { font-size: 0.75rem; font-weight: 700; color: var(--accent-brand); background: rgba(255,90,0,0.12); padding: 3px 8px; border-radius: 999px; }

    .quiz-item-card { background: rgba(9, 13, 22, 0.6); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 16px; margin-bottom: 16px; }
    .quiz-q-title { font-weight: 700; font-size: 0.95rem; color: #fff; margin-bottom: 14px; line-height: 1.45; }
    .quiz-options-grid { display: flex; flex-direction: column; gap: 8px; }
    .quiz-opt-btn {
      padding: 11px 14px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      color: var(--text-secondary);
      cursor: pointer;
      font-size: 0.88rem;
      font-weight: 500;
      text-align: left;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 44px;
    }
    .quiz-opt-btn:hover { border-color: rgba(255,255,255,0.25); background: var(--bg-card); color: #fff; }
    .quiz-opt-indicator {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid var(--text-tertiary);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-size: 0.62rem;
      font-weight: 700;
    }
    .quiz-opt-btn.correct { background: rgba(16, 185, 129, 0.15); border-color: var(--accent-emerald); color: #34d399; font-weight: 600; }
    .quiz-opt-btn.correct .quiz-opt-indicator { border-color: var(--accent-emerald); background: var(--accent-emerald); color: #fff; }
    .quiz-opt-btn.wrong { background: rgba(244, 63, 94, 0.15); border-color: var(--accent-rose); color: #fb7185; }
    .quiz-opt-btn.wrong .quiz-opt-indicator { border-color: var(--accent-rose); background: var(--accent-rose); color: #fff; }
    .quiz-feedback-box {
      margin-top: 12px;
      padding: 10px 14px;
      background: rgba(255,255,255,0.03);
      border-left: 3px solid var(--accent-brand);
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      font-size: 0.82rem;
      color: var(--text-secondary);
      display: none;
      line-height: 1.45;
    }

    /* Bottom Sticky Nav Bar */
    .bottom-nav-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-top: 28px;
      padding-top: 20px;
      border-top: 1px solid var(--border-subtle);
    }
    .nav-btn-card {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      color: var(--text-secondary);
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s;
      flex: 1;
      max-width: 48%;
      min-height: 48px;
    }
    .nav-btn-card:hover { border-color: var(--accent-brand); background: var(--bg-card-hover); color: #fff; }
    .nav-btn-label { font-size: 0.68rem; color: var(--text-tertiary); text-transform: uppercase; font-weight: 700; }
    .nav-btn-title { font-size: 0.82rem; font-weight: 700; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    /* Keyboard Shortcuts */
    .shortcuts-footer {
      display: flex;
      justify-content: center;
      gap: 16px;
      margin-top: 28px;
      font-size: 0.72rem;
      color: var(--text-tertiary);
    }
    .kbd { background: rgba(255,255,255,0.06); border: 1px solid var(--border-subtle); padding: 1px 5px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; color: var(--text-secondary); }

    /* Media Queries */
    @media (max-width: 900px) {
      :root { --sidebar-width: 320px; }
      #sidebar {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        transform: translateX(-100%);
        box-shadow: 8px 0 24px rgba(0,0,0,0.6);
      }
      #sidebar.mobile-open { transform: translateX(0); }
      .btn-close-sidebar, .btn-hamburger { display: flex; }
      .content-container { padding: 16px 16px 60px 16px; }
      .lesson-hero-title { font-size: 1.45rem; }
      .topbar { padding: 10px 14px; }
      .notes-section, .quiz-section { padding: 20px 16px; }
      .shortcuts-footer { display: none; }
      .nav-btn-card { max-width: 50%; }
    }

    @media (max-width: 480px) {
      :root { --sidebar-width: 85vw; }
      .lesson-hero-title { font-size: 1.3rem; }
      .bottom-nav-bar { flex-direction: column; }
      .nav-btn-card { width: 100%; max-width: 100%; }
      .topbar-actions .btn-done-text { display: none; }
    }
  </style>
</head>
<body>

  <div id="app-shell">
    <!-- Backdrop Overlay for Mobile -->
    <div id="mobile-backdrop" onclick="closeMobileSidebar()"></div>

    <!-- Sidebar / Drawer -->
    <aside id="sidebar">
      <div class="sidebar-header">
        <div class="brand-group">
          <div class="brand-logo">BBS</div>
          <div class="brand-info">
            <h2>Blueprint Business</h2>
            <p>Studio Suite</p>
          </div>
        </div>
        <button class="btn-close-sidebar" onclick="closeMobileSidebar()" aria-label="Close sidebar">✕</button>
      </div>

      <!-- Level Tabs Horizontal Scroll -->
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
          <input type="text" id="search-input" class="search-input" placeholder="Search 468 lessons, notes..." />
        </div>
        <div class="filter-pills">
          <button class="filter-pill active" id="filter-all" onclick="setFilter('all')">All (468)</button>
          <button class="filter-pill" id="filter-ready" onclick="setFilter('ready')">Ready to Study (99)</button>
        </div>
      </div>

      <!-- Active Level Progress -->
      <div class="level-meta-bar">
        <span class="level-title-display" id="level-active-title">Level 0: Business Model</span>
        <div class="level-prog-wrap">
          <div class="prog-bar-mini"><div class="prog-bar-fill" id="level-prog-fill" style="width: 0%;"></div></div>
          <span id="level-prog-text">0/79</span>
        </div>
      </div>

      <!-- Navigation Tree -->
      <div class="nav-list" id="nav-list"></div>
    </aside>

    <!-- Main Content Area -->
    <main id="main-content">
      <header class="topbar">
        <div class="topbar-left">
          <button class="btn-hamburger" onclick="openMobileSidebar()" aria-label="Open lessons menu">☰</button>
          <div class="breadcrumb-nav" id="breadcrumb">
            <span>Select a lesson</span>
          </div>
        </div>
        <div class="topbar-actions">
          <button class="btn btn-secondary" onclick="toggleTheaterMode()" title="Theater Mode">
            <span>⛶</span>
          </button>
          <button class="btn btn-primary" id="btn-complete-action" onclick="toggleComplete()">
            <span>✓</span> <span class="btn-done-text">Done</span>
          </button>
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
    let activeFilter = 'all';

    function renderMarkdown(md) {
      if (window.marked) return marked.parse(md || '');
      return (md || '').replace(/\\n/g, '<br/>');
    }

    const { levels, courses, chapters, modules } = window.BBS_DATA;
    let currentLevel = 0;
    let currentModuleId = null;
    let completedSet = new Set(JSON.parse(localStorage.getItem('bbs_completed') || '[]'));
    let collapsedChapters = new Set();

    function init() {
      renderLevelTabs();
      loadLevel(0);
      document.getElementById('search-input').addEventListener('input', handleSearch);

      // Keyboard navigation
      document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (e.key === ']' || e.key === 'n') goToNextModule();
        if (e.key === '[' || e.key === 'p') goToPrevModule();
        if (e.key === 'm') toggleComplete();
        if (e.key === 't') toggleTheaterMode();
      });
    }

    function setFilter(filterType) {
      activeFilter = filterType;
      document.getElementById('filter-all').classList.toggle('active', filterType === 'all');
      document.getElementById('filter-ready').classList.toggle('active', filterType === 'ready');
      renderSidebar();
    }

    function openMobileSidebar() {
      document.getElementById('sidebar').classList.add('mobile-open');
      document.getElementById('mobile-backdrop').classList.add('active');
    }

    function closeMobileSidebar() {
      document.getElementById('sidebar').classList.remove('mobile-open');
      document.getElementById('mobile-backdrop').classList.remove('active');
    }

    function renderLevelTabs() {
      const container = document.getElementById('level-tabs');
      container.innerHTML = levels.map(lvl => `
        <button class="level-tab ${lvl.level_number === currentLevel ? 'active' : ''}" 
                onclick="loadLevel(${lvl.level_number})">
          <span>L${lvl.level_number}</span>
          <span>${lvl.title || 'Level ' + lvl.level_number}</span>
        </button>
      `).join('');
    }

    function loadLevel(lvlNum) {
      currentLevel = lvlNum;
      renderLevelTabs();
      updateLevelMeta();
      renderSidebar();
      
      // Auto-select first lesson in this level (prefer ready lesson if available)
      const lvlMods = modules.filter(m => m.level_number === lvlNum);
      const firstReady = lvlMods.find(m => m.video_url || m.notes) || lvlMods[0];
      if (firstReady) selectModule(firstReady.id);
    }

    function updateLevelMeta() {
      const lvl = levels.find(l => l.level_number === currentLevel);
      const lvlMods = modules.filter(m => m.level_number === currentLevel);
      const doneCount = lvlMods.filter(m => completedSet.has(m.id)).length;
      const pct = Math.round((doneCount / lvlMods.length) * 100) || 0;

      document.getElementById('level-active-title').innerText = `Level ${currentLevel}: ${lvl ? lvl.title : ''}`;
      document.getElementById('level-prog-text').innerText = `${doneCount}/${lvlMods.length}`;
      document.getElementById('level-prog-fill').style.width = `${pct}%`;
    }

    function renderSidebar() {
      const nav = document.getElementById('nav-list');
      const lvlCourses = courses.filter(c => c.level_number === currentLevel);
      
      let html = '';
      lvlCourses.forEach(c => {
        let cMods = modules.filter(m => m.course_id === c.id);
        if (activeFilter === 'ready') {
          cMods = cMods.filter(m => m.video_url || m.notes);
          if (cMods.length === 0) return;
        }

        const releaseDate = c.release_date ? new Date(c.release_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : null;

        html += `<div class="course-group">`;
        html += `
          <div class="course-header">
            <span>${c.title}</span>
            ${releaseDate ? `<span class="course-release-tag">🗓 ${releaseDate}</span>` : ''}
          </div>
        `;

        const cChapters = chapters.filter(ch => ch.course_id === c.id);
        if (cChapters.length === 0) {
          cMods.forEach(m => html += renderModuleItem(m));
        } else {
          cChapters.forEach(ch => {
            let chMods = modules.filter(m => m.chapter_id === ch.id);
            if (activeFilter === 'ready') {
              chMods = chMods.filter(m => m.video_url || m.notes);
              if (chMods.length === 0) return;
            }

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
        }
        html += `</div>`;
      });
      nav.innerHTML = html || `<div style="text-align:center;padding:30px 10px;color:var(--text-tertiary);font-size:0.8rem;">No active modules match this filter.</div>`;
    }

    function toggleChapter(chId) {
      if (collapsedChapters.has(chId)) {
        collapsedChapters.delete(chId);
      } else {
        collapsedChapters.add(chId);
      }
      renderSidebar();
    }

    function renderModuleItem(m) {
      const isDone = completedSet.has(m.id);
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
          <div style="display:flex;align-items:center;">
            ${badge}
            ${m.duration_minutes ? `<span class="lesson-duration" style="margin-left:6px;">${m.duration_minutes}m</span>` : ''}
          </div>
        </div>
      `;
    }

    function extractVideoId(videoUrl) {
      if (!videoUrl) return null;
      const match = videoUrl.match(/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i);
      return match ? match[1] : null;
    }

    function selectModule(modId) {
      if (activeHls) {
        activeHls.destroy();
        activeHls = null;
      }

      currentModuleId = modId;
      const mod = modules.find(m => m.id === modId);
      if (!mod) return;

      renderSidebar();
      updateCompleteButton();
      updateLevelMeta();

      if (window.innerWidth <= 900) {
        closeMobileSidebar();
      }

      const crs = courses.find(c => c.id === mod.course_id);
      document.getElementById('breadcrumb').innerHTML = `
        <span class="breadcrumb-item">L${mod.level_number}</span>
        <span class="breadcrumb-sep">&rsaquo;</span>
        <span class="breadcrumb-item">${crs ? crs.title : ''}</span>
        <span class="breadcrumb-sep">&rsaquo;</span>
        <span class="breadcrumb-current">${mod.title}</span>
      `;

      const isReady = Boolean(mod.video_url || mod.notes);
      const videoId = extractVideoId(mod.video_url);

      let bodyHtml = `
        <div class="lesson-hero">
          <h1 class="lesson-hero-title">${mod.title}</h1>
          <div class="hero-tags">
            ${mod.duration_minutes ? `<span class="hero-tag tag-duration">⏱ ${mod.duration_minutes} MINS</span>` : ''}
            ${mod.video_url ? '<span class="hero-tag tag-video-live">⚡ BUNNY HD STREAM</span>' : ''}
            ${mod.notes ? '<span class="hero-tag tag-notes-live">📝 STUDY NOTES & QUIZ</span>' : ''}
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
            <div class="upcoming-icon">📅</div>
            <div class="upcoming-title">Content Scheduled for Phased Release</div>
            <div class="upcoming-desc">
              <strong>${mod.title}</strong> is part of <strong>${crs ? crs.title : 'Level ' + mod.level_number}</strong>.<br/>
              The syllabus outline is listed on the platform, and the creator is publishing video lessons according to the official timeline (Release: <em>${releaseDate}</em>).
            </div>
            <div class="upcoming-actions">
              ${nextReady ? `
                <button class="btn btn-primary" onclick="selectModule('${nextReady.id}')">
                  👉 Jump to Next Ready Lesson (${nextReady.title})
                </button>
              ` : `
                <button class="btn btn-primary" onclick="loadLevel(0)">
                  👉 Go to Level 0 (74 Video Lessons Ready)
                </button>
              `}
            </div>
          </div>
        `;
      }

      // Video Player Section
      if (videoId) {
        bodyHtml += `
          <div class="video-hero-card ${isTheater ? 'theater-mode' : ''}" id="video-card">
            <div class="video-card-topbar">
              <div class="video-stream-badge">
                <span class="stream-dot"></span>
                <span>Bunny CDN Direct HD</span>
              </div>
              <div class="video-controls-quick">
                <button class="speed-btn ${currentSpeed === 1 ? 'active' : ''}" onclick="setSpeed(1)">1x</button>
                <button class="speed-btn ${currentSpeed === 1.25 ? 'active' : ''}" onclick="setSpeed(1.25)">1.25x</button>
                <button class="speed-btn ${currentSpeed === 1.5 ? 'active' : ''}" onclick="setSpeed(1.5)">1.5x</button>
                <button class="speed-btn ${currentSpeed === 2 ? 'active' : ''}" onclick="setSpeed(2)">2x</button>
                <button class="theater-btn" onclick="toggleTheaterMode()">⛶</button>
              </div>
            </div>
            <div class="video-wrapper">
              <video id="bbs-video-player" controls playsinline preload="metadata" poster="https://vz-b7e89a3b-a06.b-cdn.net/${videoId}/thumbnail.jpg"></video>
            </div>
          </div>
        `;
      }

      // Notes Section
      if (mod.notes) {
        bodyHtml += `
          <div class="notes-section">
            <div class="notes-header-row">
              <div class="notes-title">
                <span>📚 Study Notes & Frameworks</span>
              </div>
              <button class="btn btn-secondary" style="font-size: 0.72rem; padding: 4px 8px;" onclick="copyNotes()">📋 Copy</button>
            </div>
            <div class="markdown-body" id="notes-content">
              ${renderMarkdown(mod.notes)}
            </div>
          </div>
        `;
      }

      // Quiz Section
      if (mod.quiz && mod.quiz.length > 0) {
        bodyHtml += `
          <div class="quiz-section">
            <div class="quiz-main-header">
              <div class="quiz-headline">
                <span>📝 Knowledge Check</span>
              </div>
              <div class="quiz-score-badge">${mod.quiz.length} Questions</div>
            </div>
            <div class="quiz-list">
              ${mod.quiz.map((q, qIdx) => `
                <div class="quiz-item-card">
                  <div class="quiz-q-title">${qIdx + 1}. ${q.q}</div>
                  <div class="quiz-options-grid">
                    ${q.options.map((opt, optIdx) => `
                      <button class="quiz-opt-btn" onclick="checkAnswer(this, ${optIdx}, ${q.answer}, '${escapeQuotes(q.explain || '')}')">
                        <span class="quiz-opt-indicator">${String.fromCharCode(65 + optIdx)}</span>
                        <span>${opt}</span>
                      </button>
                    `).join('')}
                  </div>
                  <div class="quiz-feedback-box" id="explain-${qIdx}"></div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }

      // Bottom Navigation
      const currentIdx = modules.findIndex(m => m.id === modId);
      const prevMod = currentIdx > 0 ? modules[currentIdx - 1] : null;
      const nextMod = currentIdx < modules.length - 1 ? modules[currentIdx + 1] : null;

      bodyHtml += `
        <div class="bottom-nav-bar">
          ${prevMod ? `
            <div class="nav-btn-card" onclick="selectModule('${prevMod.id}')">
              <span style="font-size: 1.1rem;">&larr;</span>
              <div style="overflow: hidden;">
                <div class="nav-btn-label">Prev</div>
                <div class="nav-btn-title">${prevMod.title}</div>
              </div>
            </div>
          ` : '<div></div>'}
          ${nextMod ? `
            <div class="nav-btn-card" onclick="selectModule('${nextMod.id}')" style="margin-left: auto;">
              <div style="text-align: right; overflow: hidden;">
                <div class="nav-btn-label">Next</div>
                <div class="nav-btn-title">${nextMod.title}</div>
              </div>
              <span style="font-size: 1.1rem;">&rarr;</span>
            </div>
          ` : '<div></div>'}
        </div>

        <div class="shortcuts-footer">
          <span><span class="kbd">[</span> / <span class="kbd">P</span> Prev</span>
          <span><span class="kbd">]</span> / <span class="kbd">N</span> Next</span>
          <span><span class="kbd">M</span> Done</span>
          <span><span class="kbd">T</span> Theater</span>
        </div>
      `;

      document.getElementById('content-container').innerHTML = bodyHtml;
      document.getElementById('main-content').scrollTop = 0;

      // Initialize HLS video
      if (videoId) {
        setupVideoPlayer(videoId);
      }
    }

    function setupVideoPlayer(videoId) {
      const video = document.getElementById('bbs-video-player');
      if (!video) return;

      const streamUrl = `/video-proxy/${videoId}/playlist.m3u8`;

      if (Hls.isSupported()) {
        const hls = new Hls({
          maxBufferLength: 30,
          maxMaxBufferLength: 60,
          enableWorker: true
        });
        hls.loadSource(streamUrl);
        hls.attachMedia(video);
        activeHls = hls;
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = streamUrl;
      }

      video.playbackRate = currentSpeed;
      video.addEventListener('ended', () => {
        if (currentModuleId && !completedSet.has(currentModuleId)) {
          toggleComplete();
        }
      });
    }

    function setSpeed(spd) {
      currentSpeed = spd;
      const video = document.getElementById('bbs-video-player');
      if (video) video.playbackRate = spd;
      document.querySelectorAll('.speed-btn').forEach(b => {
        b.classList.toggle('active', b.innerText === spd + 'x');
      });
    }

    function toggleTheaterMode() {
      isTheater = !isTheater;
      const card = document.getElementById('video-card');
      if (card) {
        card.classList.toggle('theater-mode', isTheater);
      }
    }

    function copyNotes() {
      const mod = modules.find(m => m.id === currentModuleId);
      if (!mod || !mod.notes) return;
      navigator.clipboard.writeText(mod.notes).then(() => {
        alert('Notes copied to clipboard!');
      });
    }

    function escapeQuotes(str) {
      return (str || '').replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
    }

    function checkAnswer(el, chosen, correct, explain) {
      const parent = el.closest('.quiz-item-card');
      const allOpts = parent.querySelectorAll('.quiz-opt-btn');
      allOpts.forEach(o => o.classList.remove('correct', 'wrong'));

      if (chosen === correct) {
        el.classList.add('correct');
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
      } else {
        completedSet.add(currentModuleId);
      }
      localStorage.setItem('bbs_completed', JSON.stringify([...completedSet]));
      updateCompleteButton();
      renderSidebar();
      updateLevelMeta();
    }

    function updateCompleteButton() {
      const btn = document.getElementById('btn-complete-action');
      if (!currentModuleId || !btn) return;
      if (completedSet.has(currentModuleId)) {
        btn.innerHTML = '<span>✓</span> <span class="btn-done-text">Done</span>';
        btn.classList.add('btn-done');
        btn.classList.remove('btn-primary');
      } else {
        btn.innerHTML = '<span>✓</span> <span class="btn-done-text">Mark Done</span>';
        btn.classList.remove('btn-done');
        btn.classList.add('btn-primary');
      }
    }

    function goToNextModule() {
      if (!currentModuleId) return;
      const idx = modules.findIndex(m => m.id === currentModuleId);
      if (idx < modules.length - 1) {
        const next = modules[idx + 1];
        if (next.level_number !== currentLevel) loadLevel(next.level_number);
        selectModule(next.id);
      }
    }

    function goToPrevModule() {
      if (!currentModuleId) return;
      const idx = modules.findIndex(m => m.id === currentModuleId);
      if (idx > 0) {
        const prev = modules[idx - 1];
        if (prev.level_number !== currentLevel) loadLevel(prev.level_number);
        selectModule(prev.id);
      }
    }

    function handleSearch(e) {
      const query = e.target.value.toLowerCase().trim();
      if (!query) {
        renderSidebar();
        return;
      }
      const matched = modules.filter(m => 
        (m.title && m.title.toLowerCase().includes(query)) || 
        (m.notes && m.notes.toLowerCase().includes(query))
      );
      const nav = document.getElementById('nav-list');
      nav.innerHTML = `
        <div class="course-header" style="color: var(--accent-emerald);">Results (${matched.length})</div>
        ${matched.map(m => renderModuleItem(m)).join('')}
      `;
    }

    init();
  </script>
</body>
</html>
"""
    with open("offline_site/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Updated BBS web app with badges and upcoming release cards!")

if __name__ == "__main__":
    build_offline_site()
