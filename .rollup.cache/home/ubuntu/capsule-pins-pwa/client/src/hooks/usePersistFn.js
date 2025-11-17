import { useRef } from "react";
/**
 * usePersistFn instead of useCallback to reduce cognitive load
 */
export function usePersistFn(fn) {
    var fnRef = useRef(fn);
    fnRef.current = fn;
    var persistFn = useRef(null);
    if (!persistFn.current) {
        persistFn.current = function () {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            return fnRef.current.apply(this, args);
        };
    }
    return persistFn.current;
}
//# sourceMappingURL=usePersistFn.js.map