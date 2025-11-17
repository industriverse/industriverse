import { __rest } from "tslib";
import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { cn } from "@/lib/utils";
function Progress(_a) {
    var className = _a.className, value = _a.value, props = __rest(_a, ["className", "value"]);
    return (<ProgressPrimitive.Root data-slot="progress" className={cn("bg-primary/20 relative h-2 w-full overflow-hidden rounded-full", className)} {...props}>
      <ProgressPrimitive.Indicator data-slot="progress-indicator" className="bg-primary h-full w-full flex-1 transition-all" style={{ transform: "translateX(-".concat(100 - (value || 0), "%)") }}/>
    </ProgressPrimitive.Root>);
}
export { Progress };
//# sourceMappingURL=progress.jsx.map