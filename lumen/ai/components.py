import param

from panel.custom import Child, JSComponent

CSS = """
.split {
    display: flex;
    flex-direction: row;
    height: 100%;
    width: 100%;
}

.gutter {
    background-color: var(--panel-surface-color);
    background-repeat: no-repeat;
    background-position: 50%;
    cursor: col-resize;
}

.gutter.gutter-horizontal {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAeCAYAAADkftS9AAAAIklEQVQoU2M4c+bMfxAGAgYYmwGrIIiDjrELjpo5aiZeMwF+yNnOs5KSvgAAAABJRU5ErkJggg==');
}

ul.nav.flex-column {
    padding-inline-start: 0 !important;
    margin: 0 !important;
}
"""


class SplitJS(JSComponent):
    """Custom component for resizable and collapsible sidebar."""

    left = Child()
    right = Child()
    sizes = param.NumericTuple(default=(60, 40), length=2)
    min_sizes = param.NumericTuple(default=(300, 200), length=2)

    _esm = """
    import Split from 'https://esm.sh/split.js@1.6.5'

    export function render({ model, view }) {
      const splitDiv = document.createElement('div');
      splitDiv.className = 'split';
      splitDiv.style.visibility = 'hidden';

      const split0 = document.createElement('div');
      const split1 = document.createElement('div');
      splitDiv.append(split0, split1);

      const splitInstance = Split([split0, split1], {
        sizes: model.sizes,
        minSize: model.min_sizes,
        gutterSize: 10,
        onDragEnd: (sizes) => {
          view.invalidate_layout();
        },
      });

      model.on("after_layout", () => {
        setTimeout(() => { splitDiv.style.visibility = 'visible'; }, 100);
      })

      split0.append(model.get_child("left"));
      split1.append(model.get_child("right"));

      return splitDiv;
    }"""

    _stylesheets = [CSS]
