import { __rest } from "tslib";
import { useDialogComposition } from "@/components/ui/dialog";
import { useComposition } from "@/hooks/useComposition";
import { cn } from "@/lib/utils";
import * as React from "react";
function Input(_a) {
    var className = _a.className, type = _a.type, onKeyDown = _a.onKeyDown, onCompositionStart = _a.onCompositionStart, onCompositionEnd = _a.onCompositionEnd, props = __rest(_a, ["className", "type", "onKeyDown", "onCompositionStart", "onCompositionEnd"]);
    // Get dialog composition context if available (will be no-op if not inside Dialog)
    var dialogComposition = useDialogComposition();
    // Add composition event handlers to support input method editor (IME) for CJK languages.
    var _b = useComposition({
        onKeyDown: function (e) {
            // Check if this is an Enter key that should be blocked
            var isComposing = e.nativeEvent.isComposing || dialogComposition.justEndedComposing();
            // If Enter key is pressed while composing or just after composition ended,
            // don't call the user's onKeyDown (this blocks the business logic)
            if (e.key === "Enter" && isComposing) {
                return;
            }
            // Otherwise, call the user's onKeyDown
            onKeyDown === null || onKeyDown === void 0 ? void 0 : onKeyDown(e);
        },
        onCompositionStart: function (e) {
            dialogComposition.setComposing(true);
            onCompositionStart === null || onCompositionStart === void 0 ? void 0 : onCompositionStart(e);
        },
        onCompositionEnd: function (e) {
            // Mark that composition just ended - this helps handle the Enter key that confirms input
            dialogComposition.markCompositionEnd();
            // Delay setting composing to false to handle Safari's event order
            // In Safari, compositionEnd fires before the ESC keydown event
            setTimeout(function () {
                dialogComposition.setComposing(false);
            }, 100);
            onCompositionEnd === null || onCompositionEnd === void 0 ? void 0 : onCompositionEnd(e);
        },
    }), handleCompositionStart = _b.onCompositionStart, handleCompositionEnd = _b.onCompositionEnd, handleKeyDown = _b.onKeyDown;
    return (<input type={type} data-slot="input" className={cn("file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm", "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]", "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive", className)} onCompositionStart={handleCompositionStart} onCompositionEnd={handleCompositionEnd} onKeyDown={handleKeyDown} {...props}/>);
}
export { Input };
//# sourceMappingURL=input.jsx.map