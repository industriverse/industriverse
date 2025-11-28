import { __rest } from "tslib";
import { cn } from "@/lib/utils";
function Skeleton(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    return (<div data-slot="skeleton" className={cn("bg-accent animate-pulse rounded-md", className)} {...props}/>);
}
export { Skeleton };
//# sourceMappingURL=skeleton.jsx.map