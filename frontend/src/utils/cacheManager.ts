/**
 * Cache Manager - Handles session storage and state invalidation
 * Clears stale data upon new project ingestion
 */

export class CacheManager {
  private static readonly CACHE_VERSION = '1.0.0';
  private static readonly VERSION_KEY = 'cartographer_cache_version';
  private static readonly PROJECT_KEY = 'current_project';
  private static readonly LAST_INGESTION_KEY = 'last_ingestion_timestamp';

  /**
   * Initialize cache manager and check for version mismatches
   */
  static initialize(): void {
    const storedVersion = localStorage.getItem(this.VERSION_KEY);
    if (storedVersion !== this.CACHE_VERSION) {
      this.clearAll();
      localStorage.setItem(this.VERSION_KEY, this.CACHE_VERSION);
    }
  }

  /**
   * Clear all cached data (session and local storage)
   */
  static clearAll(): void {
    sessionStorage.clear();
    
    // Preserve only version key
    const version = localStorage.getItem(this.VERSION_KEY);
    localStorage.clear();
    if (version) {
      localStorage.setItem(this.VERSION_KEY, version);
    }
    
    console.log('[CacheManager] All caches cleared');
  }

  /**
   * Clear cache for a specific project
   */
  static clearProject(projectName: string): void {
    const keys = Object.keys(sessionStorage);
    keys.forEach(key => {
      if (key.includes(projectName)) {
        sessionStorage.removeItem(key);
      }
    });
    
    console.log(`[CacheManager] Cleared cache for project: ${projectName}`);
  }

  /**
   * Mark new project ingestion - invalidates old project cache
   */
  static onNewIngestion(projectName: string): void {
    const currentProject = localStorage.getItem(this.PROJECT_KEY);
    
    // If switching projects, clear old project cache
    if (currentProject && currentProject !== projectName) {
      this.clearProject(currentProject);
    }
    
    localStorage.setItem(this.PROJECT_KEY, projectName);
    localStorage.setItem(this.LAST_INGESTION_KEY, Date.now().toString());
    
    console.log(`[CacheManager] New ingestion registered: ${projectName}`);
  }

  /**
   * Get cached data with expiration check
   */
  static get<T>(key: string, maxAgeMs: number = 3600000): T | null {
    const item = sessionStorage.getItem(key);
    if (!item) return null;

    try {
      const { data, timestamp } = JSON.parse(item);
      const age = Date.now() - timestamp;
      
      if (age > maxAgeMs) {
        sessionStorage.removeItem(key);
        return null;
      }
      
      return data as T;
    } catch {
      sessionStorage.removeItem(key);
      return null;
    }
  }

  /**
   * Set cached data with timestamp
   */
  static set<T>(key: string, data: T): void {
    const item = {
      data,
      timestamp: Date.now()
    };
    sessionStorage.setItem(key, JSON.stringify(item));
  }

  /**
   * Check if cache is stale for a project
   */
  static isStale(projectName: string): boolean {
    const lastIngestion = localStorage.getItem(this.LAST_INGESTION_KEY);
    const currentProject = localStorage.getItem(this.PROJECT_KEY);
    
    if (currentProject !== projectName) return true;
    if (!lastIngestion) return true;
    
    const age = Date.now() - parseInt(lastIngestion);
    return age > 86400000; // 24 hours
  }
}

// Initialize on module load
CacheManager.initialize();
