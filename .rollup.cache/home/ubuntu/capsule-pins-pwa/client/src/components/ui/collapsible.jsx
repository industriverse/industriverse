import { __rest } from "tslib";
import * as CollapsiblePrimitive from "@radix-ui/react-collapsible";
function Collapsible(_a) {
    var props = __rest(_a, []);
    return <CollapsiblePrimitive.Root data-slot="collapsible" {...props}/>;
}
function CollapsibleTrigger(_a) {
    var props = __rest(_a, []);
    return (<CollapsiblePrimitive.CollapsibleTrigger data-slot="collapsible-trigger" {...props}/>);
}
function CollapsibleContent(_a) {
    var props = __rest(_a, []);
    return (<CollapsiblePrimitive.CollapsibleContent data-slot="collapsible-content" {...props}/>);
}
export { Collapsible, CollapsibleTrigger, CollapsibleContent };
//# sourceMappingURL=collapsible.jsx.map