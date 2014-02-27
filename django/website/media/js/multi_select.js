/**********************************************************************
 *
 * A friendlier multi select widget
 *
 * Should work in: FF, Chrome, Safari, IE8+
 *
 * Depends on: lib.js
 *
 **********************************************************************/
(function ($) {
    /*
     * MultiSelect widget
     */
    function MultiSelect(el) {
        var from_select = el,
            to_select = null,
            mum = el.parentNode;

        if (el.tagName && el.tagName.toLowerCase() === "select"
                && el.getAttribute("multiple")) {
            to_select = this.buildWidget(el);

            // Attach handlers
            $(".add-item", mum).on("click", this.createAssignHandler(
                from_select, to_select));
            $(".remove-item", mum).on("click", this.createAssignHandler(
                to_select, from_select));
            while(mum.tagName.toLowerCase() !== "form" && mum.parentNode) {
                mum = mum.parentNode;
            }
            if (mum.tagName.toLowerCase() === "form") {
                $(mum).on("submit", function () {
                    // Select all options in to_select so they get saved
                    $("option", to_select).each(function (i, option) {
                        option.selected = true;
                    });
                });
            }
        }
        return this;
    }

    MultiSelect.prototype.createAssignHandler = function(from, to) {
        return function () {
            $("option", from).each(function (i, option) {
                if (option.selected) {
                    to.appendChild(
                        option.parentNode.removeChild(option)
                    );
                }
            });
        }
    }

    MultiSelect.prototype.buildWidget = function(el) {
        function createControls(add_text, remove_text) {
            var controls_html = 
                '<span class="multi-select-controls">' +
                    '<input type="button" class="btn btn-default btn-sm add-item" value="' +
                        add_text + '" />' +
                    '<input type="button" class="btn btn-default btn-sm remove-item" value="' +
                        remove_text + '" />' +
                '</span>';
            return $(controls_html)[0];
        }

        var wrap = document.createElement("div"),
            assigned = el.cloneNode(),
            mum = el.parentNode,
            add_text = el.getAttribute("data-add"),
            remove_text = el.getAttribute("data-remove"),
            $help = $(".help-text", mum),
            nodes = null;

        wrap.className = "wrap-multi-select";
        assigned.options.length = 0;

        $(["id", "name", "data-add", "data-remove"]).each(function (i, attr) {
            el.removeAttribute(attr);
        });

        // Remove selected from original and move to assigned
        $("option[selected]", el).each(function (i, option) {
            assigned.appendChild(
                option.parentNode.removeChild(option)
            );
        });

        // Build interface
        if ($help.length) { // Help text is useless now
            $help[0].parentNode.removeChild($help[0]);
        }
        wrap.appendChild(createControls(add_text, remove_text));
        wrap.appendChild(assigned);
        mum.insertBefore(wrap, el);
        mum.removeChild(el);
        wrap.insertBefore(el, wrap.firstChild);
        return assigned;
    }

    // Find and init all matching elements on this page
    $(".widget-multi-select").each(function (i, node) {
        new MultiSelect(node);
    });
})($);
