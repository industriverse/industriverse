import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-void-blue text-supernova-white p-4">
                    <div className="max-w-md w-full bg-card/60 backdrop-blur-md border border-destructive/50 rounded-lg p-6 shadow-lg text-center">
                        <div className="mb-4 flex justify-center">
                            <div className="p-3 bg-destructive/20 rounded-full">
                                <AlertTriangle className="h-8 w-8 text-destructive" />
                            </div>
                        </div>
                        <h2 className="text-xl font-bold mb-2">System Anomaly Detected</h2>
                        <p className="text-muted-foreground mb-4">
                            The consciousness engine encountered a critical error.
                        </p>
                        <div className="bg-black/50 p-4 rounded text-left text-xs font-mono overflow-auto max-h-40 mb-4 border border-white/10">
                            {this.state.error?.message}
                        </div>
                        <button
                            className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
                            onClick={() => window.location.reload()}
                        >
                            Reinitialize System
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
