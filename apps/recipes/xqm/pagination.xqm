module namespace lib = "custom/pagination";

(:
lib:paged adds paging information to a node-set
in order to enable paged results for a web-app
Will return a node with the name as specified in $nodeName
along with total number of nodes ($total), start-index ($start),
requested page-size ($num), actual page-size ($displayed)
and end-index ($end) as attributes, followed by the subsequence of the
node-set

Collection MUST be a node-set (i.e. must NOT have a root element)

If $doPaged argument is false(), only the root node with the original
collection is returned
The parameter makes it easier to do a non-conditional call of the
function on a node-set

:)

declare function lib:paged ($collection, $nodeName, $start, $pageSize, $doPaged) {
   let $total := count($collection)
   let $min := lib:max(
        lib:min(
            $pageSize,
            lib:min(
                $total,
                $total - $start + 1
            )
        )
        ,0
   )
   return
     element {$nodeName} {
       if ($doPaged) then (
        attribute total {$total},
        attribute start {$start},
        attribute pageSize {$pageSize},
        attribute actualPageSize {$min},
        attribute end {$start + $min - 1},
        subsequence($collection, $start, $pageSize)
     )
       else
        $collection
     }

};

declare function lib:min($a,$b) {
   if ($a < $b) then $a else $b
};

declare function lib:max($a,$b) {
   if ($a > $b) then $a else $b
};
