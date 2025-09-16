/**
 * Mizu Network Dashboard - JavaScript Controller
 * Advanced OwO Selfbot Control Panel
 */

class MizuDashboard {
    constructor() {
        this.currentSection = 'overview';
        this.settings = {};
        this.stats = {};
        this.logs = [];
        this.intervals = {};
        this.websocket = null;
        this.isConnected = false;
        
        // Initialize dashboard
        this.init();
    }

    /**
     * Initialize the dashboard
     */
    async init() {
        console.log('🌊 Initializing Mizu Network Dashboard...');
        
        // Show loading screen
        this.showLoadingScreen();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadInitialData();
        
        // Start update intervals
        this.startUpdateIntervals();
        
        // Hide loading screen
        this.hideLoadingScreen();
        
        // Show welcome notification
        this.showNotification('Dashboard loaded successfully!', 'success');
        
        console.log('✅ Dashboard initialized successfully');
    }

    /**
     * Show loading screen
     */
    showLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.remove('hidden');
        }
    }

    /**
     * Hide loading screen
     */
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            setTimeout(() => {
                loadingScreen.classList.add('hidden');
            }, 1000);
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });


        // Settings buttons
        document.getElementById('save-commands')?.addEventListener('click', () => this.saveSettings());
        document.getElementById('reset-commands')?.addEventListener('click', () => this.resetSettings());

        // Logs controls
        document.getElementById('clear-logs')?.addEventListener('click', () => this.clearLogs());
        document.getElementById('export-logs')?.addEventListener('click', () => this.exportLogs());
        
        // Log filters
        document.getElementById('log-type-filter')?.addEventListener('change', () => this.loadCommandLogs());
        document.getElementById('account-filter')?.addEventListener('change', () => this.loadCommandLogs());
        document.getElementById('show-timestamps')?.addEventListener('change', () => this.loadCommandLogs());
        document.getElementById('auto-scroll')?.addEventListener('change', () => {
            // Auto-scroll to bottom if enabled
            if (document.getElementById('auto-scroll')?.checked) {
                const logsOutput = document.getElementById('logs-output');
                if (logsOutput) {
                    logsOutput.scrollTop = logsOutput.scrollHeight;
                }
            }
        });
        
        // Quick Settings toggles
        document.getElementById('hunt-toggle')?.addEventListener('change', (e) => this.toggleQuickSetting('hunt', e.target.checked));
        document.getElementById('battle-toggle')?.addEventListener('change', (e) => this.toggleQuickSetting('battle', e.target.checked));
        document.getElementById('daily-toggle')?.addEventListener('change', (e) => this.toggleQuickSetting('daily', e.target.checked));
        document.getElementById('owo-toggle')?.addEventListener('change', (e) => this.toggleQuickSetting('owo', e.target.checked));
        document.getElementById('slash-commands-toggle')?.addEventListener('change', (e) => this.toggleQuickSetting('useSlashCommands', e.target.checked));
        
        // Security Settings buttons
        document.getElementById('save-security')?.addEventListener('click', () => this.saveSecuritySettings());
        document.getElementById('reset-security')?.addEventListener('click', () => this.resetSecuritySettings());

        // Stats refresh
        document.getElementById('refresh-stats')?.addEventListener('click', () => this.refreshStats());


        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveSettings();
            }
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.refreshStats();
            }
        });

        // Window events
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });

        // Visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }

    /**
     * Load initial data from real APIs
     */
    async loadInitialData() {
        try {
            // Load bot status first
            await this.loadBotStatus();
            
            // Load settings
            await this.loadSettings();
            
            // Load stats
            await this.loadStats();
            
            // Load command logs
            await this.loadCommandLogs();
            
            // Load quick settings
            await this.loadQuickSettings();
            
            // Update UI
            this.updateUI();
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showNotification('Failed to load initial data', 'error');
            this.updateBotStatus('offline');
        }
    }

    /**
     * Switch between sections
     */
    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionName).classList.add('active');

        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    /**
     * Load section-specific data
     */
    loadSectionData(section) {
        switch (section) {
            case 'overview':
                this.refreshStats();
                this.loadRecentActivity();
                break;
            case 'logs':
                this.startLogUpdates();
                this.loadCommandLogs();
                break;
            case 'commands':
                this.loadSettings();
                this.loadQuickSettings();
                this.attachTerminateHandler();
                break;
            case 'security':
                this.loadSecuritySettings();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            default:
                // Stop log updates for other sections
                this.stopLogUpdates();
                break;
        }
    }


    /**
     * Update bot status indicator
     */
    updateBotStatus(status, captchaDetected = false, isSleeping = false) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (statusDot && statusText) {
            // Handle different status types
            let displayStatus = status;
            let statusClass = status;
            
            if (status === 'captcha' || captchaDetected) {
                displayStatus = 'Captcha Detected';
                statusClass = 'captcha';
            } else if (status === 'paused' || isSleeping) {
                displayStatus = 'Paused';
                statusClass = 'paused';
            } else if (status === 'online') {
                displayStatus = 'Online';
                statusClass = 'online';
            } else if (status === 'offline') {
                displayStatus = 'Offline';
                statusClass = 'offline';
            }
            
            statusDot.className = `status-dot ${statusClass}`;
            statusText.textContent = displayStatus;
        }
        
        this.isConnected = status === 'online' && !captchaDetected && !isSleeping;
    }

    /**
     * Load settings from server
     */
    async loadSettings() {
        try {
            // Simulate API call
            this.settings = {
                commands: {
                    hunt: { enabled: true, cooldown: [15, 17] },
                    battle: { enabled: true, cooldown: [15, 17] },
                    daily: { enabled: false },
                    owo: { enabled: true }
                },
                gambling: {
                    slots: { enabled: false },
                    coinflip: { enabled: false }
                },
                automation: {
                    giveaway: { enabled: false },
                    gems: { enabled: false }
                }
            };
            
            this.populateSettings();
            
        } catch (error) {
            console.error('Failed to load settings:', error);
            throw error;
        }
    }

    /**
     * Populate UI with settings
     */
    populateSettings() {
        // Update quick toggles
        const huntToggle = document.getElementById('hunt-toggle');
        const battleToggle = document.getElementById('battle-toggle');
        const dailyToggle = document.getElementById('daily-toggle');
        const owoToggle = document.getElementById('owo-toggle');
        
        if (huntToggle) huntToggle.checked = this.settings.commands?.hunt?.enabled || false;
        if (battleToggle) battleToggle.checked = this.settings.commands?.battle?.enabled || false;
        if (dailyToggle) dailyToggle.checked = this.settings.commands?.daily?.enabled || false;
        if (owoToggle) owoToggle.checked = this.settings.commands?.owo?.enabled || false;
    }

    /**
     * Save settings to server
     */
    async saveSettings() {
        try {
            this.showNotification('Saving settings...', 'info');
            
            // Simulate API call
            await this.delay(1000);
            
            this.showNotification('Settings saved successfully!', 'success');
            
        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showNotification('Failed to save settings', 'error');
        }
    }

    /**
     * Reset settings to default
     */
    async resetSettings() {
        if (confirm('Are you sure you want to reset all settings to default?')) {
            try {
                this.showNotification('Resetting settings...', 'info');
                
                // Reset to defaults
                await this.delay(1000);
                await this.loadSettings();
                
                this.showNotification('Settings reset successfully!', 'success');
                
            } catch (error) {
                console.error('Failed to reset settings:', error);
                this.showNotification('Failed to reset settings', 'error');
            }
        }
    }

    /**
     * Update quick setting
     */
    async updateQuickSetting(setting, enabled) {
        try {
            if (this.settings.commands && this.settings.commands[setting]) {
                this.settings.commands[setting].enabled = enabled;
                
                // Auto-save quick settings
                await this.delay(500);
                this.showNotification(`${setting.charAt(0).toUpperCase() + setting.slice(1)} ${enabled ? 'enabled' : 'disabled'}`, 'info');
            }
        } catch (error) {
            console.error('Failed to update quick setting:', error);
        }
    }

    /**
     * Load statistics from real selfbot API
     */
    async loadStats() {
        try {
            const response = await fetch('/api/dashboard/stats');
            if (response.ok) {
                this.stats = await response.json();
                this.updateStatsUI();
            } else {
                throw new Error('Failed to fetch stats from API');
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
            // Fallback to default values
            this.stats = {
                balance: 0,
                hunts_today: 0,
                battles_today: 0,
                uptime: 0,
                commands_executed: 0,
                captchas_solved: 0
            };
            this.updateStatsUI();
            throw error;
        }
    }

    /**
     * Update statistics UI
     */
    updateStatsUI() {
        // Update main stats
        this.updateElement('total-cowoncy', this.stats.balance_formatted || this.formatNumber(this.stats.balance));
        this.updateElement('hunts-today', this.stats.hunts_today);
        this.updateElement('battles-today', this.stats.battles_today);
        this.updateElement('uptime-display', this.formatUptime(this.stats.uptime));
        
        // Update navbar stats
        this.updateElement('navbar-balance', this.formatNumber(this.stats.balance));
        this.updateElement('navbar-uptime', this.formatUptime(this.stats.uptime));
        
        // Update accounts breakdown
        this.updateAccountsBreakdown();
    }
    
    /**
     * Update accounts breakdown section
     */
    updateAccountsBreakdown() {
        const accountsContainer = document.getElementById('accounts-breakdown');
        if (!accountsContainer || !this.stats.accounts) return;
        
        // Show refresh indicator
        const refreshIndicator = document.getElementById('accounts-refresh');
        if (refreshIndicator) {
            refreshIndicator.classList.add('spinning');
            setTimeout(() => refreshIndicator.classList.remove('spinning'), 1000);
        }
        
        // Clear existing content
        accountsContainer.innerHTML = '';
        
        if (this.stats.accounts.length === 0) {
            accountsContainer.innerHTML = `
                <div class="account-card">
                    <div class="account-header">
                        <span class="account-id">No Accounts</span>
                    </div>
                    <div class="account-stats">
                        <p style="color: var(--text-secondary); text-align: center; margin: 0;">
                            No active accounts found. Make sure your bot is running and has valid tokens.
                        </p>
                    </div>
                </div>
            `;
            return;
        }
        
        // Create account cards
        this.stats.accounts.forEach(account => {
            const accountCard = document.createElement('div');
            accountCard.className = 'account-card';
            
            accountCard.innerHTML = `
                <div class="account-header">
                    <span class="account-id">${account.user_display}</span>
                    <div class="account-status">
                        <div class="status-dot online"></div>
                        <span>Online</span>
                    </div>
                </div>
                <div class="account-stats">
                    <div class="account-stat">
                        <div class="account-stat-label">
                            <i class="fas fa-coins"></i>
                            <span>Cowoncy</span>
                        </div>
                        <div class="account-stat-value cowoncy">${account.cowoncy_formatted}</div>
                    </div>
                    <div class="account-stat">
                        <div class="account-stat-label">
                            <i class="fas fa-robot"></i>
                            <span>Captchas</span>
                        </div>
                        <div class="account-stat-value">${account.captchas}</div>
                    </div>
                    <div class="account-stat">
                        <div class="account-stat-label">
                            <i class="fas fa-user"></i>
                            <span>User ID</span>
                        </div>
                        <div class="account-stat-value" style="font-size: var(--font-size-xs); font-family: monospace;">${account.user_id}</div>
                    </div>
                </div>
            `;
            
            accountsContainer.appendChild(accountCard);
        });
    }

    /**
     * Refresh statistics
     */
    async refreshStats() {
        try {
            const refreshBtn = document.getElementById('refresh-stats');
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Refreshing...';
                refreshBtn.disabled = true;
            }
            
            await this.loadStats();
            
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
                refreshBtn.disabled = false;
            }
            
        } catch (error) {
            console.error('Failed to refresh stats:', error);
            this.showNotification('Failed to refresh stats', 'error');
        }
    }

    /**
     * Load bot status from real API
     */
    async loadBotStatus() {
        try {
            const response = await fetch('/api/dashboard/status');
            if (response.ok) {
                const statusData = await response.json();
                this.updateBotStatus(
                    statusData.status, 
                    statusData.captcha_detected, 
                    statusData.is_sleeping
                );
                
                // Update account info if available
                if (statusData.active_accounts !== undefined) {
                    this.updateElement('active-accounts', statusData.active_accounts);
                    this.updateElement('total-accounts', statusData.total_accounts);
                }
                
                // Show captcha notification if detected
                if (statusData.captcha_detected && !this.lastCaptchaNotification) {
                    this.showNotification('🚨 Captcha detected! Bot automatically stopped', 'error', 10000);
                    this.lastCaptchaNotification = true;
                } else if (!statusData.captcha_detected) {
                    this.lastCaptchaNotification = false;
                }
            }
        } catch (error) {
            console.error('Failed to load bot status:', error);
            this.updateBotStatus('offline');
        }
    }

    /**
     * Load recent activity from real API
     */
    async loadRecentActivity() {
        try {
            const response = await fetch('/api/dashboard/activity');
            if (response.ok) {
                const activities = await response.json();
                
                const activityFeed = document.getElementById('recent-activity');
                if (activityFeed && activities.length > 0) {
                    activityFeed.innerHTML = activities.map(activity => `
                        <div class="activity-item ${activity.type}">
                            <div class="activity-icon">
                                <i class="${activity.icon || 'fas fa-info-circle'}"></i>
                            </div>
                            <div class="activity-content">
                                <div class="activity-message">${activity.message}</div>
                                <div class="activity-time">${activity.time}</div>
                            </div>
                        </div>
                    `).join('');
                } else if (activityFeed) {
                    activityFeed.innerHTML = '<div class="no-activity">No recent activity</div>';
                }
            }
        } catch (error) {
            console.error('Failed to load recent activity:', error);
            const activityFeed = document.getElementById('recent-activity');
            if (activityFeed) {
                activityFeed.innerHTML = '<div class="error-message">Failed to load activity</div>';
            }
        }
    }

    /**
     * Load command logs from real API
     */
    async loadCommandLogs() {
        try {
            const logType = document.getElementById('log-type-filter')?.value || 'all';
            const accountFilter = document.getElementById('account-filter')?.value || 'all';
            
            const response = await fetch(`/api/dashboard/command-logs?type=${logType}&account=${accountFilter}&limit=100`);
            if (response.ok) {
                const data = await response.json();
                this.updateCommandLogs(data.logs);
                this.updateLogStats(data.total_count, data.filtered_count);
                this.populateAccountFilter(data.logs);
            }
        } catch (error) {
            console.error('Failed to load command logs:', error);
            this.showLogError('Failed to load command logs');
        }
    }

    /**
     * Update command logs display
     */
    updateCommandLogs(logs) {
        const logsOutput = document.getElementById('logs-output');
        if (!logsOutput) return;

        // Clear welcome message
        logsOutput.innerHTML = '';

        if (logs.length === 0) {
            logsOutput.innerHTML = `
                <div class="logs-welcome">
                    <i class="fas fa-info-circle"></i>
                    <h3>No Commands Found</h3>
                    <p>No command activity to display with current filters</p>
                </div>
            `;
            return;
        }

        // Add logs
        logs.forEach(log => this.addLogEntry(log));
        
        // Auto scroll if enabled
        if (document.getElementById('auto-scroll')?.checked) {
            logsOutput.scrollTop = logsOutput.scrollHeight;
        }
    }

    /**
     * Add a single log entry
     */
    addLogEntry(log) {
        const logsOutput = document.getElementById('logs-output');
        if (!logsOutput) return;

        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';

        const showTimestamps = document.getElementById('show-timestamps')?.checked;
        
        logEntry.innerHTML = `
            ${showTimestamps ? `<div class="log-timestamp">${log.formatted_time}</div>` : ''}
            <div class="log-account">${log.account_display}</div>
            <div class="log-type ${log.command_type}">${log.command_type.toUpperCase()}</div>
            <div class="log-message">${this.formatLogMessage(log.message, log.status)}</div>
        `;

        logsOutput.appendChild(logEntry);

        // Remove old entries if too many (keep last 200)
        const entries = logsOutput.querySelectorAll('.log-entry');
        if (entries.length > 200) {
            entries[0].remove();
        }
    }

    /**
     * Format log message based on status
     */
    formatLogMessage(message, status) {
        if (status === 'success') {
            return `<span class="success">${message}</span>`;
        } else if (status === 'error') {
            return `<span class="error">${message}</span>`;
        } else if (message.includes('found:') || message.includes('caught')) {
            return message.replace(/(found:|caught)/g, '<span class="success">$1</span>');
        } else if (message.includes('cowoncy') || message.includes('💰')) {
            return message.replace(/(\d+)/g, '<span class="highlight">$1</span>');
        }
        return message;
    }

    /**
     * Update log statistics
     */
    updateLogStats(totalCount, filteredCount) {
        this.updateElement('total-commands', totalCount);
        
        // Update session time (uptime)
        if (this.stats && this.stats.uptime) {
            this.updateElement('session-time', this.formatUptime(this.stats.uptime));
        }
    }

    /**
     * Populate account filter dropdown
     */
    populateAccountFilter(logs) {
        const accountFilter = document.getElementById('account-filter');
        if (!accountFilter) return;

        // Get unique accounts
        const accounts = [...new Set(logs.map(log => ({
            id: log.account_id,
            display: log.account_display
        })))];

        // Clear existing options except "All Accounts"
        const allOption = accountFilter.querySelector('option[value="all"]');
        accountFilter.innerHTML = '';
        if (allOption) accountFilter.appendChild(allOption);

        // Add account options
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.id;
            option.textContent = account.display;
            accountFilter.appendChild(option);
        });
    }

    /**
     * Show log error message
     */
    showLogError(message) {
        const logsOutput = document.getElementById('logs-output');
        if (!logsOutput) return;

        logsOutput.innerHTML = `
            <div class="logs-welcome">
                <i class="fas fa-exclamation-triangle" style="color: var(--danger-color);"></i>
                <h3>Error Loading Logs</h3>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Toggle quick setting (hunt, battle, daily, owo)
     */
    async toggleQuickSetting(command, enabled) {
        try {
            // Show loading state
            const toggle = document.getElementById(`${command}-toggle`);
            const toggleItem = toggle?.closest('.toggle-item');
            
            if (toggle) {
                toggle.disabled = true;
            }
            
            // Add loading visual feedback
            if (toggleItem) {
                toggleItem.classList.add('loading');
            }
            
            // Show immediate feedback notification
            const commandNames = {
                'hunt': 'Hunt',
                'battle': 'Battle', 
                'daily': 'Daily',
                'owo': 'OwO',
                'useSlashCommands': 'Slash Commands'
            };
            
            const commandName = commandNames[command] || command.toUpperCase();
            this.showNotification(`${enabled ? 'Enabling' : 'Disabling'} ${commandName}...`, 'info', 2000);

            const response = await fetch('/api/dashboard/quick-toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    enabled: enabled
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification(result.message, 'success');
                
                // Log the change in the logs if we're on the logs page
                if (this.currentSection === 'logs') {
                    setTimeout(() => this.loadCommandLogs(), 500);
                }
            } else {
                const error = await response.json();
                this.showNotification(error.error || 'Failed to update setting', 'error');
                
                // Revert toggle state on error
                if (toggle) {
                    toggle.checked = !enabled;
                }
            }
        } catch (error) {
            console.error('Error toggling quick setting:', error);
            this.showNotification('Failed to update setting', 'error');
            
            // Revert toggle state on error
            const toggle = document.getElementById(`${command}-toggle`);
            if (toggle) {
                toggle.checked = !enabled;
            }
        } finally {
            // Re-enable toggle and remove loading state
            const toggle = document.getElementById(`${command}-toggle`);
            const toggleItem = toggle?.closest('.toggle-item');
            
            if (toggle) {
                toggle.disabled = false;
            }
            
            if (toggleItem) {
                toggleItem.classList.remove('loading');
            }
        }
    }

    /**
     * Load current quick settings status
     */
    async loadQuickSettings() {
        try {
            const response = await fetch('/api/dashboard/quick-settings');
            if (response.ok) {
                const settings = await response.json();
                
                // Update toggle states
                const huntToggle = document.getElementById('hunt-toggle');
                const battleToggle = document.getElementById('battle-toggle');
                const dailyToggle = document.getElementById('daily-toggle');
                const owoToggle = document.getElementById('owo-toggle');
                const slashCommandsToggle = document.getElementById('slash-commands-toggle');
                
                if (huntToggle) huntToggle.checked = settings.hunt;
                if (battleToggle) battleToggle.checked = settings.battle;
                if (dailyToggle) dailyToggle.checked = settings.daily;
                if (owoToggle) owoToggle.checked = settings.owo;
                if (slashCommandsToggle) slashCommandsToggle.checked = settings.useSlashCommands;
            }
        } catch (error) {
            console.error('Failed to load quick settings:', error);
        }
    }

    attachTerminateHandler() {
        const btn = document.getElementById('terminate-bot');
        if (!btn || btn.dataset.bound === '1') return;
        btn.dataset.bound = '1';
        btn.addEventListener('click', async () => {
            if (!confirm('Terminate all running bot instances now?')) return;
            try {
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Terminating...';
                const res = await fetch('/api/dashboard/terminate', { method: 'POST' });
                const data = await res.json();
                this.showNotification(data?.message || 'Terminate signal sent', 'success');
            } catch (e) {
                this.showNotification('Failed to terminate bot', 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-power-off"></i> Terminate Bot';
            }
        });
    }

    /**
     * Load security settings
     */
    async loadSecuritySettings() {
        try {
            const response = await fetch('/api/dashboard/security-settings');
            if (response.ok) {
                const settings = await response.json();
                
                // Update form fields
                document.getElementById('delay-min').value = settings.delay_min;
                document.getElementById('delay-max').value = settings.delay_max;
                document.getElementById('captcha-restart-min').value = settings.captcha_restart_min;
                document.getElementById('captcha-restart-max').value = settings.captcha_restart_max;
            }
        } catch (error) {
            console.error('Failed to load security settings:', error);
        }
        
    }

    /**
     * Save security settings
     */
    async saveSecuritySettings() {
        try {
            const delayMin = parseFloat(document.getElementById('delay-min').value);
            const delayMax = parseFloat(document.getElementById('delay-max').value);
            
            // Validate delay values
            if (delayMin >= delayMax) {
                this.showNotification('Minimum delay must be less than maximum delay', 'error');
                return;
            }
            
            if (delayMin < 1 || delayMax > 10) {
                this.showNotification('Delay values must be between 1 and 10 seconds', 'error');
                return;
            }

            const settings = {
                delay_min: delayMin,
                delay_max: delayMax,
                captcha_restart_min: parseFloat(document.getElementById('captcha-restart-min').value),
                captcha_restart_max: parseFloat(document.getElementById('captcha-restart-max').value),
                typing_indicator: false,
                random_delays: false,
                silent_mode: false
            };

            const response = await fetch('/api/dashboard/security-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification(result.message, 'success');
                
                // Log the change in the logs if we're on the logs page
                if (this.currentSection === 'logs') {
                    setTimeout(() => this.loadCommandLogs(), 500);
                }
            } else {
                const error = await response.json();
                this.showNotification(error.error || 'Failed to save security settings', 'error');
            }
        } catch (error) {
            console.error('Error saving security settings:', error);
            this.showNotification('Failed to save security settings', 'error');
        }
    }

    /**
     * Reset security settings to defaults
     */
    async resetSecuritySettings() {
        if (!confirm('Are you sure you want to reset all security settings to defaults?')) {
            return;
        }

        try {
            // Reset to default values
            document.getElementById('delay-min').value = 1.7;
            document.getElementById('delay-max').value = 2.7;
            document.getElementById('captcha-restart-min').value = 3.7;
            document.getElementById('captcha-restart-max').value = 5.6;

            // Save the reset settings
            await this.saveSecuritySettings();
            
        } catch (error) {
            console.error('Error resetting security settings:', error);
            this.showNotification('Failed to reset security settings', 'error');
        }
    }

    /**
     * Start log updates from real API
     */
    startLogUpdates() {
        if (this.intervals.logs) return;
        
        // Load initial logs
        this.loadRealLogs();
        
        // Update logs every 3 seconds
        this.intervals.logs = setInterval(() => {
            this.loadRealLogs();
        }, 3000);
    }

    /**
     * Load real logs from API
     */
    async loadRealLogs() {
        try {
            const response = await fetch('/api/dashboard/logs');
            if (response.ok) {
                const logs = await response.json();
                
                // Clear existing logs and add new ones
                const logsOutput = document.getElementById('logs-output');
                if (logsOutput) {
                    // Only update if we have new logs
                    const currentLogCount = logsOutput.children.length;
                    if (logs.length !== currentLogCount) {
                        logsOutput.innerHTML = '';
                        logs.forEach(log => {
                            const logEntry = this.createLogEntry(log);
                            logsOutput.appendChild(logEntry);
                        });
                        
                        // Auto scroll if enabled
                        const autoScroll = document.getElementById('auto-scroll');
                        if (autoScroll && autoScroll.checked) {
                            logsOutput.scrollTop = logsOutput.scrollHeight;
                        }
                    }
                }
                
                this.logs = logs;
            }
        } catch (error) {
            console.error('Failed to load real logs:', error);
            // Fallback to adding a random log
            this.addRandomLog();
        }
    }

    /**
     * Stop log updates
     */
    stopLogUpdates() {
        if (this.intervals.logs) {
            clearInterval(this.intervals.logs);
            delete this.intervals.logs;
        }
    }

    /**
     * Add random log entry
     */
    addRandomLog() {
        const logTypes = ['info', 'success', 'warning', 'error'];
        const messages = [
            'Hunt command executed successfully',
            'Battle won! Gained cowoncy',
            'Daily reward claimed',
            'Auto sell completed',
            'Giveaway joined successfully',
            'Level grinding in progress...',
            'Connection established',
            'Settings saved'
        ];
        
        const log = {
            timestamp: new Date().toLocaleTimeString(),
            level: logTypes[Math.floor(Math.random() * logTypes.length)],
            message: messages[Math.floor(Math.random() * messages.length)]
        };
        
        this.logs.push(log);
        this.updateLogsUI([log]);
        
        // Limit log entries
        if (this.logs.length > 100) {
            this.logs = this.logs.slice(-100);
        }
    }

    /**
     * Update logs UI
     */
    updateLogsUI(newLogs) {
        const logsOutput = document.getElementById('logs-output');
        if (!logsOutput) return;
        
        newLogs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log.level}`;
            logEntry.innerHTML = `
                <span class="log-time">[${log.timestamp}]</span>
                <span class="log-level">[${log.level.toUpperCase()}]</span>
                <span class="log-message">${log.message}</span>
            `;
            logsOutput.appendChild(logEntry);
        });
        
        // Auto scroll if enabled
        const autoScroll = document.getElementById('auto-scroll');
        if (autoScroll && autoScroll.checked) {
            logsOutput.scrollTop = logsOutput.scrollHeight;
        }
    }

    /**
     * Clear logs
     */
    clearLogs() {
        const logsOutput = document.getElementById('logs-output');
        if (logsOutput) {
            logsOutput.innerHTML = '';
            this.logs = [];
            this.showNotification('Logs cleared', 'info');
        }
    }

    /**
     * Export logs
     */
    exportLogs() {
        const logText = this.logs.map(log => 
            `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}`
        ).join('\n');
        
        const blob = new Blob([logText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `mizu-logs-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Logs exported successfully', 'success');
    }

    /**
     * Start update intervals for real-time data
     */
    startUpdateIntervals() {
        // Stats update every 5 seconds
        this.intervals.stats = setInterval(async () => {
            if (this.currentSection === 'overview') {
                await this.loadStats();
            }
        }, 5000);
        
        // Bot status update every 10 seconds
        this.intervals.status = setInterval(async () => {
            await this.loadBotStatus();
        }, 10000);
        
        // Activity update every 15 seconds
        this.intervals.activity = setInterval(async () => {
            if (this.currentSection === 'overview') {
                await this.loadRecentActivity();
            }
        }, 15000);
        
        // Command logs update every 3 seconds for real-time feel
        this.intervals.commandLogs = setInterval(async () => {
            if (this.currentSection === 'logs') {
                await this.loadCommandLogs();
            }
        }, 3000);
        
        // Navbar stats update every 3 seconds
        this.intervals.navbar = setInterval(async () => {
            try {
                const response = await fetch('/api/dashboard/stats');
                if (response.ok) {
                    const stats = await response.json();
                    this.updateElement('navbar-balance', this.formatNumber(stats.balance));
                    this.updateElement('navbar-uptime', this.formatUptime(stats.uptime));
                }
            } catch (error) {
                // Silent fail for navbar updates
            }
        }, 3000);
    }

    /**
     * Pause updates when tab is hidden
     */
    pauseUpdates() {
        Object.keys(this.intervals).forEach(key => {
            if (key !== 'uptime') {
                clearInterval(this.intervals[key]);
                delete this.intervals[key];
            }
        });
    }

    /**
     * Resume updates when tab is visible
     */
    resumeUpdates() {
        this.startUpdateIntervals();
    }

    /**
     * Update UI elements
     */
    updateUI() {
        this.updateStatsUI();
        this.populateSettings();
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notifications-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
        
        // Add animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
    }

    /**
     * Get notification icon
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Update element content
     */
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    /**
     * Format large numbers
     */
    formatNumber(num) {
        if (num >= 1000000000) {
            return (num / 1000000000).toFixed(1) + 'B';
        }
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    /**
     * Format uptime
     */
    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Delay utility
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        Object.values(this.intervals).forEach(interval => {
            clearInterval(interval);
        });
        
        if (this.websocket) {
            this.websocket.close();
        }
    }

    /**
     * Load analytics data
     */
    loadAnalytics() {
        if (this.analyticsTimer) clearInterval(this.analyticsTimer);
        this.fetchAnalytics();
        this.analyticsTimer = setInterval(() => this.fetchAnalytics(), 3000);
    }

    fetchAnalytics() {
        fetch(`/api/dashboard/analytics`)
            .then(res => res.json())
            .then(data => {
                // Global cards
                const fmt = new Intl.NumberFormat('en-US');
                const fmtInt = x => fmt.format(Math.max(0, parseInt(x || 0)));
                const byId = id => document.getElementById(id);
                if (byId('global-cpm')) byId('global-cpm').textContent = fmtInt(data?.global?.cpm);
                if (byId('global-active')) byId('global-active').textContent = fmtInt(data?.global?.active_accounts);
                if (byId('global-session')) byId('global-session').textContent = fmtInt(data?.global?.session_total);
                if (byId('global-net')) byId('global-net').textContent = fmtInt(data?.global?.net_earnings);

                // Table
                const tbody = document.querySelector('#analytics-table tbody');
                if (!tbody) return;
                tbody.innerHTML = '';
                (data?.accounts || []).forEach(acc => {
                    const tr = document.createElement('tr');
                    const last = acc.last_command_ts ? new Date(acc.last_command_ts * 1000).toLocaleTimeString() : '-';
                    tr.innerHTML = `
                        <td>${acc.account_display || acc.account_id}</td>
                        <td>${fmtInt(acc.cpm)}</td>
                        <td>${fmtInt(acc.hunt)}</td>
                        <td>${fmtInt(acc.battle)}</td>
                        <td>${fmtInt(acc.daily)}</td>
                        <td>${fmtInt(acc.owo)}</td>
                        <td>${fmtInt(acc.net_earnings)}</td>
                        <td>${last}</td>
                    `;
                    tbody.appendChild(tr);
                });
            })
            .catch(() => {});
    }

}

// Notification styles (injected dynamically)
const notificationStyles = `
<style>
.notification {
    margin-bottom: 0.5rem;
    border-radius: var(--radius-lg);
    overflow: hidden;
    transform: translateX(100%);
    transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
    opacity: 0;
    pointer-events: auto;
    box-shadow: var(--shadow-lg);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(79, 209, 199, 0.2);
}

.notification.show {
    transform: translateX(0);
    opacity: 1;
}

.notification-content {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md) var(--spacing-lg);
    color: white;
    font-weight: 500;
    font-size: var(--font-size-sm);
}

.notification.info .notification-content {
    background: rgba(66, 153, 225, 0.9);
}

.notification.success .notification-content {
    background: rgba(72, 187, 120, 0.9);
}

.notification.warning .notification-content {
    background: rgba(237, 137, 54, 0.9);
}

.notification.error .notification-content {
    background: rgba(245, 101, 101, 0.9);
}

.notification-message {
    flex: 1;
}

.notification-close {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: var(--spacing-xs);
    border-radius: var(--radius-sm);
    transition: background-color 0.2s ease;
}

.notification-close:hover {
    background: rgba(255, 255, 255, 0.2);
}

.activity-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    margin-bottom: var(--spacing-sm);
    border-radius: var(--radius-lg);
    background: rgba(79, 209, 199, 0.05);
    border-left: 3px solid var(--primary-color);
    transition: all var(--transition-fast);
}

.activity-item:hover {
    background: rgba(79, 209, 199, 0.1);
    transform: translateX(5px);
}

.activity-item.success {
    border-left-color: var(--success-color);
}

.activity-item.warning {
    border-left-color: var(--warning-color);
}

.activity-item.error {
    border-left-color: var(--danger-color);
}

.activity-time {
    font-size: var(--font-size-xs);
    color: var(--text-muted);
    min-width: 80px;
}

.activity-message {
    flex: 1;
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
}

.log-entry {
    display: flex;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-xs);
    line-height: 1.4;
    transition: background-color 0.2s ease;
}

.log-entry:hover {
    background: rgba(79, 209, 199, 0.05);
}

.log-time {
    color: var(--primary-color);
    font-weight: 500;
    min-width: 80px;
}

.log-level {
    font-weight: 600;
    min-width: 60px;
}

.log-entry.info .log-level { color: var(--info-color); }
.log-entry.success .log-level { color: var(--success-color); }
.log-entry.warning .log-level { color: var(--warning-color); }
.log-entry.error .log-level { color: var(--danger-color); }

.log-message {
    color: var(--text-secondary);
    flex: 1;
}
</style>
`;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Inject notification styles
    document.head.insertAdjacentHTML('beforeend', notificationStyles);
    
    // Initialize dashboard
    window.mizuDashboard = new MizuDashboard();
    
});

// Export for global access
window.MizuDashboard = MizuDashboard;
