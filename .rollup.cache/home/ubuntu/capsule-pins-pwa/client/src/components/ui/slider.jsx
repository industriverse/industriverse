import { __rest } from "tslib";
import * as React from "react";
import * as SliderPrimitive from "@radix-ui/react-slider";
import { cn } from "@/lib/utils";
function Slider(_a) {
    var className = _a.className, defaultValue = _a.defaultValue, value = _a.value, _b = _a.min, min = _b === void 0 ? 0 : _b, _c = _a.max, max = _c === void 0 ? 100 : _c, props = __rest(_a, ["className", "defaultValue", "value", "min", "max"]);
    var _values = React.useMemo(function () {
        return Array.isArray(value)
            ? value
            : Array.isArray(defaultValue)
                ? defaultValue
                : [min, max];
    }, [value, defaultValue, min, max]);
    return (<SliderPrimitive.Root data-slot="slider" defaultValue={defaultValue} value={value} min={min} max={max} className={cn("relative flex w-full touch-none items-center select-none data-[disabled]:opacity-50 data-[orientation=vertical]:h-full data-[orientation=vertical]:min-h-44 data-[orientation=vertical]:w-auto data-[orientation=vertical]:flex-col", className)} {...props}>
      <SliderPrimitive.Track data-slot="slider-track" className={cn("bg-muted relative grow overflow-hidden rounded-full data-[orientation=horizontal]:h-1.5 data-[orientation=horizontal]:w-full data-[orientation=vertical]:h-full data-[orientation=vertical]:w-1.5")}>
        <SliderPrimitive.Range data-slot="slider-range" className={cn("bg-primary absolute data-[orientation=horizontal]:h-full data-[orientation=vertical]:w-full")}/>
      </SliderPrimitive.Track>
      {Array.from({ length: _values.length }, function (_, index) { return (<SliderPrimitive.Thumb data-slot="slider-thumb" key={index} className="border-primary ring-ring/50 block size-4 shrink-0 rounded-full border bg-white shadow-sm transition-[color,box-shadow] hover:ring-4 focus-visible:ring-4 focus-visible:outline-hidden disabled:pointer-events-none disabled:opacity-50"/>); })}
    </SliderPrimitive.Root>);
}
export { Slider };
//# sourceMappingURL=slider.jsx.map