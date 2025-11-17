import { __rest } from "tslib";
import * as React from "react";
import * as PopoverPrimitive from "@radix-ui/react-popover";
import { cn } from "@/lib/utils";
function Popover(_a) {
    var props = __rest(_a, []);
    return <PopoverPrimitive.Root data-slot="popover" {...props}/>;
}
function PopoverTrigger(_a) {
    var props = __rest(_a, []);
    return <PopoverPrimitive.Trigger data-slot="popover-trigger" {...props}/>;
}
function PopoverContent(_a) {
    var className = _a.className, _b = _a.align, align = _b === void 0 ? "center" : _b, _c = _a.sideOffset, sideOffset = _c === void 0 ? 4 : _c, props = __rest(_a, ["className", "align", "sideOffset"]);
    return (<PopoverPrimitive.Portal>
      <PopoverPrimitive.Content data-slot="popover-content" align={align} sideOffset={sideOffset} className={cn("bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 w-72 origin-(--radix-popover-content-transform-origin) rounded-md border p-4 shadow-md outline-hidden", className)} {...props}/>
    </PopoverPrimitive.Portal>);
}
function PopoverAnchor(_a) {
    var props = __rest(_a, []);
    return <PopoverPrimitive.Anchor data-slot="popover-anchor" {...props}/>;
}
export { Popover, PopoverTrigger, PopoverContent, PopoverAnchor };
//# sourceMappingURL=popover.jsx.map