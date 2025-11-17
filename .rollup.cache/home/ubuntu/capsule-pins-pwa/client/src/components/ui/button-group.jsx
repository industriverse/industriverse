import { __rest } from "tslib";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { Separator } from "@/components/ui/separator";
var buttonGroupVariants = cva("flex w-fit items-stretch [&>*]:focus-visible:z-10 [&>*]:focus-visible:relative [&>[data-slot=select-trigger]:not([class*='w-'])]:w-fit [&>input]:flex-1 has-[select[aria-hidden=true]:last-child]:[&>[data-slot=select-trigger]:last-of-type]:rounded-r-md has-[>[data-slot=button-group]]:gap-2", {
    variants: {
        orientation: {
            horizontal: "[&>*:not(:first-child)]:rounded-l-none [&>*:not(:first-child)]:border-l-0 [&>*:not(:last-child)]:rounded-r-none",
            vertical: "flex-col [&>*:not(:first-child)]:rounded-t-none [&>*:not(:first-child)]:border-t-0 [&>*:not(:last-child)]:rounded-b-none",
        },
    },
    defaultVariants: {
        orientation: "horizontal",
    },
});
function ButtonGroup(_a) {
    var className = _a.className, orientation = _a.orientation, props = __rest(_a, ["className", "orientation"]);
    return (<div role="group" data-slot="button-group" data-orientation={orientation} className={cn(buttonGroupVariants({ orientation: orientation }), className)} {...props}/>);
}
function ButtonGroupText(_a) {
    var className = _a.className, _b = _a.asChild, asChild = _b === void 0 ? false : _b, props = __rest(_a, ["className", "asChild"]);
    var Comp = asChild ? Slot : "div";
    return (<Comp className={cn("bg-muted flex items-center gap-2 rounded-md border px-4 text-sm font-medium shadow-xs [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4", className)} {...props}/>);
}
function ButtonGroupSeparator(_a) {
    var className = _a.className, _b = _a.orientation, orientation = _b === void 0 ? "vertical" : _b, props = __rest(_a, ["className", "orientation"]);
    return (<Separator data-slot="button-group-separator" orientation={orientation} className={cn("bg-input relative !m-0 self-stretch data-[orientation=vertical]:h-auto", className)} {...props}/>);
}
export { ButtonGroup, ButtonGroupSeparator, ButtonGroupText, buttonGroupVariants, };
//# sourceMappingURL=button-group.jsx.map