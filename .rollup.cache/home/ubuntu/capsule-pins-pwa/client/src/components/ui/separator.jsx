import { __rest } from "tslib";
import * as React from "react";
import * as SeparatorPrimitive from "@radix-ui/react-separator";
import { cn } from "@/lib/utils";
function Separator(_a) {
    var className = _a.className, _b = _a.orientation, orientation = _b === void 0 ? "horizontal" : _b, _c = _a.decorative, decorative = _c === void 0 ? true : _c, props = __rest(_a, ["className", "orientation", "decorative"]);
    return (<SeparatorPrimitive.Root data-slot="separator" decorative={decorative} orientation={orientation} className={cn("bg-border shrink-0 data-[orientation=horizontal]:h-px data-[orientation=horizontal]:w-full data-[orientation=vertical]:h-full data-[orientation=vertical]:w-px", className)} {...props}/>);
}
export { Separator };
//# sourceMappingURL=separator.jsx.map