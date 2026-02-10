// Type definitions for Dive AI window API

interface DiveAPIGateway {
    request(endpoint: string, data?: any): Promise<any>;
    chat(message: string, options?: { system?: string; model_id?: string; conversation_id?: string }): Promise<{
        response?: string;
        error?: string;
        model?: string;
        tokens?: number;
        latency_ms?: number;
        thinking?: string;
        actions?: Array<{
            action: string;
            success: boolean;
            output: string;
            error: string;
        }>;
        self_heal_rounds?: number;
        conversation_id?: string;
    }>;
    health(): Promise<{
        status: 'healthy' | 'unhealthy';
        version: string;
        timestamp: string;
        llm: {
            provider: string;
            models: number;
            available: boolean;
            primary: string;
        };
        automation: boolean;
    }>;
    models(): Promise<{
        provider: string;
        models: Array<{
            id: string;
            name: string;
            model: string;
            priority: number;
            thinking: boolean;
        }>;
        total: number;
    }>;
}

interface DiveAPIAutomation {
    screenshot(): Promise<{
        screenshot: string;
        size: { width: number; height: number };
        timestamp: string;
    }>;
    click(x: number, y: number): Promise<{ status: string; action: string }>;
    type(text: string): Promise<{ status: string; action: string }>;
    execute(action: string, params: any): Promise<any>;
}

interface DiveAPITerminal {
    execute(command: string, cwd?: string): Promise<{
        output: string;
        error: string;
        code: number;
    }>;
}

interface DiveAPIFileSystem {
    read(path: string): Promise<{ content: string; path: string }>;
    write(path: string, content: string): Promise<{ success: boolean; path: string }>;
    readFile(path: string): Promise<{ content: string; path: string }>;
    writeFile(path: string, content: string): Promise<{ success: boolean; path: string }>;
}

interface DiveAPI {
    gateway: DiveAPIGateway;
    automation: DiveAPIAutomation;
    terminal: DiveAPITerminal;
    fs: DiveAPIFileSystem;
}

declare global {
    interface Window {
        diveAPI: DiveAPI;
    }
}

export { };
