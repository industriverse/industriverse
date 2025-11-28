import { __rest } from "tslib";
import { cn } from "@/lib/utils";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { XIcon } from "lucide-react";
import * as React from "react";
// Context to track composition state across dialog children
var DialogCompositionContext = React.createContext({
    isComposing: function () { return false; },
    setComposing: function () { },
    justEndedComposing: function () { return false; },
    markCompositionEnd: function () { },
});
export var useDialogComposition = function () {
    return React.useContext(DialogCompositionContext);
};
function Dialog(_a) {
    var props = __rest(_a, []);
    var composingRef = React.useRef(false);
    var justEndedRef = React.useRef(false);
    var endTimerRef = React.useRef(null);
    var contextValue = React.useMemo(function () { return ({
        isComposing: function () { return composingRef.current; },
        setComposing: function (composing) {
            composingRef.current = composing;
        },
        justEndedComposing: function () { return justEndedRef.current; },
        markCompositionEnd: function () {
            justEndedRef.current = true;
            if (endTimerRef.current) {
                clearTimeout(endTimerRef.current);
            }
            endTimerRef.current = setTimeout(function () {
                justEndedRef.current = false;
            }, 150);
        },
    }); }, []);
    return (<DialogCompositionContext.Provider value={contextValue}>
      <DialogPrimitive.Root data-slot="dialog" {...props}/>
    </DialogCompositionContext.Provider>);
}
function DialogTrigger(_a) {
    var props = __rest(_a, []);
    return <DialogPrimitive.Trigger data-slot="dialog-trigger" {...props}/>;
}
function DialogPortal(_a) {
    var props = __rest(_a, []);
    return <DialogPrimitive.Portal data-slot="dialog-portal" {...props}/>;
}
function DialogClose(_a) {
    var props = __rest(_a, []);
    return <DialogPrimitive.Close data-slot="dialog-close" {...props}/>;
}
function DialogOverlay(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    return (<DialogPrimitive.Overlay data-slot="dialog-overlay" className={cn("data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/50", className)} {...props}/>);
}
DialogOverlay.displayName = "DialogOverlay";
function DialogContent(_a) {
    var className = _a.className, children = _a.children, _b = _a.showCloseButton, showCloseButton = _b === void 0 ? true : _b, onEscapeKeyDown = _a.onEscapeKeyDown, props = __rest(_a, ["className", "children", "showCloseButton", "onEscapeKeyDown"]);
    var isComposing = useDialogComposition().isComposing;
    var handleEscapeKeyDown = React.useCallback(function (e) {
        // Check both the native isComposing property and our context state
        // This handles Safari's timing issues with composition events
        var isCurrentlyComposing = e.isComposing || isComposing();
        // If IME is composing, prevent dialog from closing
        if (isCurrentlyComposing) {
            e.preventDefault();
            return;
        }
        // Call user's onEscapeKeyDown if provided
        onEscapeKeyDown === null || onEscapeKeyDown === void 0 ? void 0 : onEscapeKeyDown(e);
    }, [isComposing, onEscapeKeyDown]);
    return (<DialogPortal data-slot="dialog-portal">
      <DialogOverlay />
      <DialogPrimitive.Content data-slot="dialog-content" className={cn("bg-background data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 fixed top-[50%] left-[50%] z-50 grid w-full max-w-[calc(100%-2rem)] translate-x-[-50%] translate-y-[-50%] gap-4 rounded-lg border p-6 shadow-lg duration-200 sm:max-w-lg", className)} onEscapeKeyDown={handleEscapeKeyDown} {...props}>
        {children}
        {showCloseButton && (<DialogPrimitive.Close data-slot="dialog-close" className="ring-offset-background focus:ring-ring data-[state=open]:bg-accent data-[state=open]:text-muted-foreground absolute top-4 right-4 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus:ring-2 focus:ring-offset-2 focus:outline-hidden disabled:pointer-events-none [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4">
            <XIcon />
            <span className="sr-only">Close</span>
          </DialogPrimitive.Close>)}
      </DialogPrimitive.Content>
    </DialogPortal>);
}
function DialogHeader(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    return (<div data-slot="dialog-header" className={cn("flex flex-col gap-2 text-center sm:text-left", className)} {...props}/>);
}
function DialogFooter(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    return (<div data-slot="dialog-footer" className={cn("flex flex-col-reverse gap-2 sm:flex-row sm:justify-end", className)} {...props}/>);
}
function DialogTitle(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    return (<DialogPrimitive.Title data-slot="dialog-title" className={cn("text-lg leading-none font-semibold", className)} {...props}/>);
}
function DialogDescription(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    return (<DialogPrimitive.Description data-slot="dialog-description" className={cn("text-muted-foreground text-sm", className)} {...props}/>);
}
export { Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogOverlay, DialogPortal, DialogTitle, DialogTrigger };
//# sourceMappingURL=dialog.jsx.map