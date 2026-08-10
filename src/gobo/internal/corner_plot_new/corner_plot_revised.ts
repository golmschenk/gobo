import {Column, ColumnView} from 'models/layouts/column'
import * as p from 'core/properties'

export class CornerPlotView extends ColumnView {
  declare model: CornerPlot
}

export namespace CornerPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Column.Props
}

export interface CornerPlot extends CornerPlot.Attrs {}

export class CornerPlot extends Column {
  declare properties: CornerPlot.Props
  declare __view_type__: CornerPlotView

  constructor(attrs?: Partial<CornerPlot.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = CornerPlotView
  }
}