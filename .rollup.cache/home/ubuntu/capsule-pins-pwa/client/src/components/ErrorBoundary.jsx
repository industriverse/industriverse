import { __extends } from "tslib";
import { cn } from "@/lib/utils";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { Component } from "react";
var ErrorBoundary = /** @class */ (function (_super) {
    __extends(ErrorBoundary, _super);
    function ErrorBoundary(props) {
        var _this = _super.call(this, props) || this;
        _this.state = { hasError: false, error: null };
        return _this;
    }
    ErrorBoundary.getDerivedStateFromError = function (error) {
        return { hasError: true, error: error };
    };
    ErrorBoundary.prototype.render = function () {
        var _a;
        if (this.state.hasError) {
            return (<div className="flex items-center justify-center min-h-screen p-8 bg-background">
          <div className="flex flex-col items-center w-full max-w-2xl p-8">
            <AlertTriangle size={48} className="text-destructive mb-6 flex-shrink-0"/>

            <h2 className="text-xl mb-4">An unexpected error occurred.</h2>

            <div className="p-4 w-full rounded bg-muted overflow-auto mb-6">
              <pre className="text-sm text-muted-foreground whitespace-break-spaces">
                {(_a = this.state.error) === null || _a === void 0 ? void 0 : _a.stack}
              </pre>
            </div>

            <button onClick={function () { return window.location.reload(); }} className={cn("flex items-center gap-2 px-4 py-2 rounded-lg", "bg-primary text-primary-foreground", "hover:opacity-90 cursor-pointer")}>
              <RotateCcw size={16}/>
              Reload Page
            </button>
          </div>
        </div>);
        }
        return this.props.children;
    };
    return ErrorBoundary;
}(Component));
export default ErrorBoundary;
//# sourceMappingURL=ErrorBoundary.jsx.map