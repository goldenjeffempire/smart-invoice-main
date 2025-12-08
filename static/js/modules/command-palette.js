/**
 * InvoiceFlow Command Palette
 * Quick navigation and actions via keyboard shortcuts
 */

import Utils from './utils.js';

class CommandPalette {
  constructor() {
    this.isOpen = false;
    this.commands = [];
    this.filteredCommands = [];
    this.selectedIndex = 0;
    this.container = null;
    this.searchInput = null;
    this.commandsList = null;
    this.init();
  }

  init() {
    this.createUI();
    this.registerDefaultCommands();
    this.bindEvents();
  }

  createUI() {
    this.container = document.createElement('div');
    this.container.className = 'command-palette';
    this.container.setAttribute('role', 'dialog');
    this.container.setAttribute('aria-modal', 'true');
    this.container.setAttribute('aria-label', 'Command palette');
    this.container.innerHTML = `
      <div class="command-palette-backdrop"></div>
      <div class="command-palette-content">
        <div class="command-palette-header">
          <svg class="command-palette-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
          <input 
            type="text" 
            class="command-palette-search" 
            placeholder="Type a command or search..."
            autocomplete="off"
            spellcheck="false"
          />
          <kbd class="command-palette-shortcut">ESC</kbd>
        </div>
        <div class="command-palette-results">
          <ul class="command-palette-list" role="listbox"></ul>
          <div class="command-palette-empty">
            <span>No results found</span>
          </div>
        </div>
        <div class="command-palette-footer">
          <div class="command-palette-hint">
            <kbd>&uarr;</kbd><kbd>&darr;</kbd> Navigate
            <kbd>&crarr;</kbd> Select
            <kbd>ESC</kbd> Close
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(this.container);
    this.searchInput = this.container.querySelector('.command-palette-search');
    this.commandsList = this.container.querySelector('.command-palette-list');
    this.backdrop = this.container.querySelector('.command-palette-backdrop');
  }

  registerDefaultCommands() {
    this.register([
      {
        id: 'home',
        title: 'Go to Home',
        category: 'Navigation',
        icon: 'home',
        action: () => window.location.href = '/'
      },
      {
        id: 'dashboard',
        title: 'Go to Dashboard',
        category: 'Navigation',
        icon: 'dashboard',
        action: () => window.location.href = '/dashboard/'
      },
      {
        id: 'invoices',
        title: 'View All Invoices',
        category: 'Navigation',
        icon: 'file-text',
        action: () => window.location.href = '/invoices/'
      },
      {
        id: 'create-invoice',
        title: 'Create New Invoice',
        category: 'Actions',
        icon: 'plus',
        shortcut: 'N',
        action: () => window.location.href = '/invoices/new/'
      },
      {
        id: 'analytics',
        title: 'View Analytics',
        category: 'Navigation',
        icon: 'chart',
        action: () => window.location.href = '/invoices/analytics/'
      },
      {
        id: 'templates',
        title: 'Invoice Templates',
        category: 'Navigation',
        icon: 'template',
        action: () => window.location.href = '/invoices/templates/'
      },
      {
        id: 'profile',
        title: 'Edit Profile',
        category: 'Settings',
        icon: 'user',
        action: () => window.location.href = '/settings/profile/'
      },
      {
        id: 'settings',
        title: 'Account Settings',
        category: 'Settings',
        icon: 'settings',
        action: () => window.location.href = '/settings/'
      },
      {
        id: 'logout',
        title: 'Sign Out',
        category: 'Account',
        icon: 'logout',
        action: () => window.location.href = '/logout/'
      },
      {
        id: 'theme-toggle',
        title: 'Toggle Dark Mode',
        category: 'Preferences',
        icon: 'moon',
        action: () => {
          document.documentElement.classList.toggle('dark');
          localStorage.setItem('theme', 
            document.documentElement.classList.contains('dark') ? 'dark' : 'light'
          );
        }
      },
      {
        id: 'help',
        title: 'Help & Support',
        category: 'Help',
        icon: 'help',
        action: () => window.location.href = '/support/'
      },
      {
        id: 'shortcuts',
        title: 'Keyboard Shortcuts',
        category: 'Help',
        icon: 'keyboard',
        action: () => this.showShortcuts()
      }
    ]);
  }

  register(commands) {
    this.commands.push(...commands);
    this.filteredCommands = [...this.commands];
  }

  bindEvents() {
    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.toggle();
      }

      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });

    this.backdrop.addEventListener('click', () => this.close());

    this.searchInput.addEventListener('input', () => {
      this.filter(this.searchInput.value);
    });

    this.searchInput.addEventListener('keydown', (e) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          this.selectNext();
          break;
        case 'ArrowUp':
          e.preventDefault();
          this.selectPrevious();
          break;
        case 'Enter':
          e.preventDefault();
          this.executeSelected();
          break;
      }
    });

    this.commandsList.addEventListener('click', (e) => {
      const item = e.target.closest('.command-palette-item');
      if (item) {
        const index = parseInt(item.dataset.index);
        this.executeCommand(this.filteredCommands[index]);
      }
    });

    this.commandsList.addEventListener('mousemove', (e) => {
      const item = e.target.closest('.command-palette-item');
      if (item) {
        const index = parseInt(item.dataset.index);
        if (index !== this.selectedIndex) {
          this.selectedIndex = index;
          this.updateSelection();
        }
      }
    });
  }

  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  open() {
    this.isOpen = true;
    this.container.classList.add('open');
    this.searchInput.value = '';
    this.filter('');
    this.selectedIndex = 0;
    
    requestAnimationFrame(() => {
      this.searchInput.focus();
    });

    document.body.style.overflow = 'hidden';
  }

  close() {
    this.isOpen = false;
    this.container.classList.remove('open');
    document.body.style.overflow = '';
  }

  filter(query) {
    const normalizedQuery = query.toLowerCase().trim();

    if (!normalizedQuery) {
      this.filteredCommands = [...this.commands];
    } else {
      this.filteredCommands = this.commands.filter(cmd => {
        const titleMatch = cmd.title.toLowerCase().includes(normalizedQuery);
        const categoryMatch = cmd.category?.toLowerCase().includes(normalizedQuery);
        return titleMatch || categoryMatch;
      }).sort((a, b) => {
        const aStart = a.title.toLowerCase().startsWith(normalizedQuery);
        const bStart = b.title.toLowerCase().startsWith(normalizedQuery);
        if (aStart && !bStart) return -1;
        if (!aStart && bStart) return 1;
        return 0;
      });
    }

    this.selectedIndex = 0;
    this.render();
  }

  render() {
    const emptyState = this.container.querySelector('.command-palette-empty');
    
    if (this.filteredCommands.length === 0) {
      this.commandsList.innerHTML = '';
      emptyState.style.display = 'block';
      return;
    }

    emptyState.style.display = 'none';
    
    const groupedCommands = this.groupByCategory(this.filteredCommands);
    let html = '';
    let globalIndex = 0;

    for (const [category, commands] of Object.entries(groupedCommands)) {
      html += `<li class="command-palette-category">${Utils.escape(category)}</li>`;
      
      for (const cmd of commands) {
        const isSelected = globalIndex === this.selectedIndex;
        html += `
          <li 
            class="command-palette-item ${isSelected ? 'selected' : ''}" 
            role="option"
            data-index="${globalIndex}"
            aria-selected="${isSelected}"
          >
            <span class="command-item-icon">${this.getIcon(cmd.icon)}</span>
            <span class="command-item-title">${Utils.escape(cmd.title)}</span>
            ${cmd.shortcut ? `<kbd class="command-item-shortcut">${cmd.shortcut}</kbd>` : ''}
          </li>
        `;
        globalIndex++;
      }
    }

    this.commandsList.innerHTML = html;
  }

  groupByCategory(commands) {
    return commands.reduce((acc, cmd) => {
      const category = cmd.category || 'General';
      if (!acc[category]) acc[category] = [];
      acc[category].push(cmd);
      return acc;
    }, {});
  }

  getIcon(iconName) {
    const icons = {
      home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
      dashboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
      'file-text': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
      plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
      chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
      template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>',
      user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
      settings: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
      logout: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
      moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
      help: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
      keyboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2" ry="2"/><line x1="6" y1="8" x2="6" y2="8"/><line x1="10" y1="8" x2="10" y2="8"/><line x1="14" y1="8" x2="14" y2="8"/><line x1="18" y1="8" x2="18" y2="8"/><line x1="8" y1="12" x2="8" y2="12"/><line x1="12" y1="12" x2="12" y2="12"/><line x1="16" y1="12" x2="16" y2="12"/><line x1="7" y1="16" x2="17" y2="16"/></svg>'
    };
    return icons[iconName] || icons.help;
  }

  selectNext() {
    if (this.selectedIndex < this.filteredCommands.length - 1) {
      this.selectedIndex++;
      this.updateSelection();
    }
  }

  selectPrevious() {
    if (this.selectedIndex > 0) {
      this.selectedIndex--;
      this.updateSelection();
    }
  }

  updateSelection() {
    const items = this.commandsList.querySelectorAll('.command-palette-item');
    items.forEach((item, index) => {
      const isSelected = index === this.selectedIndex;
      item.classList.toggle('selected', isSelected);
      item.setAttribute('aria-selected', isSelected);
      
      if (isSelected) {
        item.scrollIntoView({ block: 'nearest' });
      }
    });
  }

  executeSelected() {
    const command = this.filteredCommands[this.selectedIndex];
    if (command) {
      this.executeCommand(command);
    }
  }

  executeCommand(command) {
    this.close();
    if (command.action) {
      command.action();
    }
  }

  showShortcuts() {
    const modal = document.createElement('div');
    modal.className = 'shortcuts-modal';
    modal.innerHTML = `
      <div class="shortcuts-modal-backdrop"></div>
      <div class="shortcuts-modal-content">
        <h3>Keyboard Shortcuts</h3>
        <div class="shortcuts-list">
          <div class="shortcut-item">
            <span>Open Command Palette</span>
            <kbd>Ctrl/Cmd + K</kbd>
          </div>
          <div class="shortcut-item">
            <span>Create New Invoice</span>
            <kbd>N</kbd>
          </div>
          <div class="shortcut-item">
            <span>Go to Dashboard</span>
            <kbd>G then D</kbd>
          </div>
          <div class="shortcut-item">
            <span>Go to Invoices</span>
            <kbd>G then I</kbd>
          </div>
          <div class="shortcut-item">
            <span>Close Modal/Palette</span>
            <kbd>ESC</kbd>
          </div>
        </div>
        <button class="shortcuts-modal-close">Close</button>
      </div>
    `;

    document.body.appendChild(modal);

    const close = () => modal.remove();
    modal.querySelector('.shortcuts-modal-backdrop').addEventListener('click', close);
    modal.querySelector('.shortcuts-modal-close').addEventListener('click', close);
    document.addEventListener('keydown', function handler(e) {
      if (e.key === 'Escape') {
        close();
        document.removeEventListener('keydown', handler);
      }
    });
  }
}

export const commandPalette = new CommandPalette();
export default commandPalette;
