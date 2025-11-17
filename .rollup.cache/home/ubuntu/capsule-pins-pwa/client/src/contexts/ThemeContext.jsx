import React, { createContext, useContext, useEffect, useState } from "react";
var ThemeContext = createContext(undefined);
export function ThemeProvider(_a) {
    var children = _a.children, _b = _a.defaultTheme, defaultTheme = _b === void 0 ? "light" : _b, _c = _a.switchable, switchable = _c === void 0 ? false : _c;
    var _d = useState(function () {
        if (switchable) {
            var stored = localStorage.getItem("theme");
            return stored || defaultTheme;
        }
        return defaultTheme;
    }), theme = _d[0], setTheme = _d[1];
    useEffect(function () {
        var root = document.documentElement;
        if (theme === "dark") {
            root.classList.add("dark");
        }
        else {
            root.classList.remove("dark");
        }
        if (switchable) {
            localStorage.setItem("theme", theme);
        }
    }, [theme, switchable]);
    var toggleTheme = switchable
        ? function () {
            setTheme(function (prev) { return (prev === "light" ? "dark" : "light"); });
        }
        : undefined;
    return (<ThemeContext.Provider value={{ theme: theme, toggleTheme: toggleTheme, switchable: switchable }}>
      {children}
    </ThemeContext.Provider>);
}
export function useTheme() {
    var context = useContext(ThemeContext);
    if (!context) {
        throw new Error("useTheme must be used within ThemeProvider");
    }
    return context;
}
//# sourceMappingURL=ThemeContext.jsx.map