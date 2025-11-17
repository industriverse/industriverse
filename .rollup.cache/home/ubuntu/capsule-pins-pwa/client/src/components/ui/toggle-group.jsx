"use client";
import { __rest } from "tslib";
import * as React from "react";
import * as ToggleGroupPrimitive from "@radix-ui/react-toggle-group";
import { cn } from "@/lib/utils";
import { toggleVariants } from "@/components/ui/toggle";
var ToggleGroupContext = React.createContext({
    size: "default",
    variant: "default",
});
function ToggleGroup(_a) {
    var className = _a.className, variant = _a.variant, size = _a.size, children = _a.children, props = __rest(_a, ["className", "variant", "size", "children"]);
    return (<ToggleGroupPrimitive.Root data-slot="toggle-group" data-variant={variant} data-size={size} className={cn("group/toggle-group flex w-fit items-center rounded-md data-[variant=outline]:shadow-xs", className)} {...props}>
      <ToggleGroupContext.Provider value={{ variant: variant, size: size }}>
        {children}
      </ToggleGroupContext.Provider>
    </ToggleGroupPrimitive.Root>);
}
function ToggleGroupItem(_a) {
    var className = _a.className, children = _a.children, variant = _a.variant, size = _a.size, props = __rest(_a, ["className", "children", "variant", "size"]);
    var context = React.useContext(ToggleGroupContext);
    return (<ToggleGroupPrimitive.Item data-slot="toggle-group-item" data-variant={context.variant || variant} data-size={context.size || size} className={cn(toggleVariants({
            variant: context.variant || variant,
            size: context.size || size,
        }), "min-w-0 flex-1 shrink-0 rounded-none shadow-none first:rounded-l-md last:rounded-r-md focus:z-10 focus-visible:z-10 data-[variant=outline]:border-l-0 data-[variant=outline]:first:border-l", className)} {...props}>
      {children}
    </ToggleGroupPrimitive.Item>);
}
export { ToggleGroup, ToggleGroupItem };
//# sourceMappingURL=toggle-group.jsx.map