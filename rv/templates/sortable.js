(function () {
        var idCounter = 0;

        function getValueFromCell(cell) {
            if (cell.dataset.num) {
                return parseFloat(cell.dataset.num);
            }
            return cell.innerHTML;
        }

        function getRowObjFromRow(row, cellSelector) {
            if (!row.dataset.sortId) {
                row.dataset.sortId = (idCounter++);
            }
            var cell = row.querySelector(cellSelector);
            var value = getValueFromCell(cell);
            return {
                tr: row,
                datum: value,
                sortId: parseInt(row.dataset.sortId)
            };
        }

        function sortByColumn(table, colIndex, descending) {
            descending = (descending ? -1 : 1);
            var selector = "td:nth-child(" + (colIndex + 1) + ")";
            var tbody = table.querySelector("tbody");
            var rowObjs = [].slice.call(tbody.querySelectorAll("tr")).map(function (row) {
                return getRowObjFromRow(row, selector);
            }).sort(function (rowObj1, rowObj2) {
                if (rowObj1.datum < rowObj2.datum) return -descending;
                if (rowObj1.datum > rowObj2.datum) return +descending;
                return (rowObj2.sortId - rowObj1.sortId); // Ensure stable sort
            });
            rowObjs.forEach(function (rowObj) {
                var row = rowObj.tr;
                if (row.parentNode) {
                    row.parentNode.removeChild(row);
                }
                tbody.appendChild(row);
            });
        }

        function makeTableSortable(table) {
            table.querySelectorAll("thead th").forEach(function (th, i) {
                th.appendChild(document.createTextNode(' '));
                th.appendChild(Object.assign(document.createElement('a'), {
                    innerHTML: '\u2191',
                    href: '#',
                    onclick: function (event) {
                        sortByColumn(table, i, false);
                        event.preventDefault();
                    },
                }));
                th.appendChild(Object.assign(document.createElement('a'), {
                    innerHTML: '\u2193',
                    href: '#',
                    onclick: function (event) {
                        sortByColumn(table, i, true);
                        event.preventDefault();
                    },
                }));
            });
        }

        window.addEventListener("load", function () {
            [].slice.call(document.querySelectorAll("table.sortable")).forEach(makeTableSortable);
        }, false);
    }
    ()
)
;
