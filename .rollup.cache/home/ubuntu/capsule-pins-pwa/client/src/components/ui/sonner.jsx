import { __rest } from "tslib";
import { useTheme } from "next-themes";
import { Toaster as Sonner } from "sonner";
var Toaster = function (_a) {
    var props = __rest(_a, []);
    var _b = useTheme().theme, theme = _b === void 0 ? "system" : _b;
    return (<Sonner theme={theme} className="toaster group" style={{
            "--normal-bg": "var(--popover)",
            "--normal-text": "var(--popover-foreground)",
            "--normal-border": "var(--border)",
        }} {...props}/>);
};
export { Toaster };
//# sourceMappingURL=sonner.jsx.map