import { __rest } from "tslib";
import * as React from "react";
import * as HoverCardPrimitive from "@radix-ui/react-hover-card";
import { cn } from "@/lib/utils";
function HoverCard(_a) {
    var props = __rest(_a, []);
    return <HoverCardPrimitive.Root data-slot="hover-card" {...props}/>;
}
function HoverCardTrigger(_a) {
    var props = __rest(_a, []);
    return (<HoverCardPrimitive.Trigger data-slot="hover-card-trigger" {...props}/>);
}
function HoverCardContent(_a) {
    var className = _a.className, _b = _a.align, align = _b === void 0 ? "center" : _b, _c = _a.sideOffset, sideOffset = _c === void 0 ? 4 : _c, props = __rest(_a, ["className", "align", "sideOffset"]);
    return (<HoverCardPrimitive.Portal data-slot="hover-card-portal">
      <HoverCardPrimitive.Content data-slot="hover-card-content" align={align} sideOffset={sideOffset} className={cn("bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 w-64 origin-(--radix-hover-card-content-transform-origin) rounded-md border p-4 shadow-md outline-hidden", className)} {...props}/>
    </HoverCardPrimitive.Portal>);
}
export { HoverCard, HoverCardTrigger, HoverCardContent };
//# sourceMappingURL=hover-card.jsx.map