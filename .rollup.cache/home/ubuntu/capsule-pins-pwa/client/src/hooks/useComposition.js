import { useRef } from "react";
import { usePersistFn } from "./usePersistFn";
export function useComposition(options) {
    if (options === void 0) { options = {}; }
    var originalOnKeyDown = options.onKeyDown, originalOnCompositionStart = options.onCompositionStart, originalOnCompositionEnd = options.onCompositionEnd;
    var c = useRef(false);
    var timer = useRef(null);
    var timer2 = useRef(null);
    var onCompositionStart = usePersistFn(function (e) {
        if (timer.current) {
            clearTimeout(timer.current);
            timer.current = null;
        }
        if (timer2.current) {
            clearTimeout(timer2.current);
            timer2.current = null;
        }
        c.current = true;
        originalOnCompositionStart === null || originalOnCompositionStart === void 0 ? void 0 : originalOnCompositionStart(e);
    });
    var onCompositionEnd = usePersistFn(function (e) {
        // 使用两层 setTimeout 来处理 Safari 浏览器中 compositionEnd 先于 onKeyDown 触发的问题
        timer.current = setTimeout(function () {
            timer2.current = setTimeout(function () {
                c.current = false;
            });
        });
        originalOnCompositionEnd === null || originalOnCompositionEnd === void 0 ? void 0 : originalOnCompositionEnd(e);
    });
    var onKeyDown = usePersistFn(function (e) {
        // 在 composition 状态下，阻止 ESC 和 Enter（非 shift+Enter）事件的冒泡
        if (c.current &&
            (e.key === "Escape" || (e.key === "Enter" && !e.shiftKey))) {
            e.stopPropagation();
            return;
        }
        originalOnKeyDown === null || originalOnKeyDown === void 0 ? void 0 : originalOnKeyDown(e);
    });
    var isComposing = usePersistFn(function () {
        return c.current;
    });
    return {
        onCompositionStart: onCompositionStart,
        onCompositionEnd: onCompositionEnd,
        onKeyDown: onKeyDown,
        isComposing: isComposing,
    };
}
//# sourceMappingURL=useComposition.js.map