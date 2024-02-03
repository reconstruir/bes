#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_cli_args(_test_simple_lexer_mixin, program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_make_mmd(self):
    tmp = self.make_temp_file(suffix = '.mmd')
    args = [
      'btl',
      'lexer_make_mmd',
      self._simple_lexer_desc_filename,
      tmp,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assert_text_file_equal_fuzzy( '''
stateDiagram-v2
  direction LR
    
  %% s_start state
  [*] --> s_start
  s_start --> s_done: c_eos
  s_start --> s_start: c_nl
  s_start --> s_start: c_ws
  s_start --> s_key: c_keyval_key_first
  s_start --> s_done: default

  %% s_key state
  s_key --> s_key: c_keyval_key
  s_key --> s_value: c_equal
  s_key --> s_done: c_eos
    
  %% s_value state
  s_value --> s_start: c_nl
  s_value --> s_done: c_eos
  s_value --> s_value: default
    
  %% s_done state
  s_done --> [*]    
  ''', tmp )

  def test_make_diagram(self):
    tmp = self.make_temp_file(suffix = '.svg')
    args = [
      'btl',
      'lexer_make_diagram',
      '--format', 'svg',
      self._simple_lexer_desc_filename,
      tmp,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    from bes.fs.file_util import file_util
    print(file_util.read(tmp, codec = 'utf-8'))
    return
    self.assert_text_file_equal_fuzzy( '''
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="mermaid-svg" width="100%" class="statediagram" style="max-width: 966.265625px;" viewBox="0 0 966.265625 313.5" role="graphics-document document" aria-roledescription="stateDiagram">
  <style>#mermaid-svg{font-family:"trebuchet ms",verdana,arial,sans-serif;font-size:16px;fill:#333;}#mermaid-svg .error-icon{fill:#552222;}#mermaid-svg .error-text{fill:#552222;stroke:#552222;}#mermaid-svg .edge-thickness-normal{stroke-width:2px;}#mermaid-svg .edge-thickness-thick{stroke-width:3.5px;}#mermaid-svg .edge-pattern-solid{stroke-dasharray:0;}#mermaid-svg .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-svg .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-svg .marker{fill:#333333;stroke:#333333;}#mermaid-svg .marker.cross{stroke:#333333;}#mermaid-svg svg{font-family:"trebuchet ms",verdana,arial,sans-serif;font-size:16px;}#mermaid-svg defs #statediagram-barbEnd{fill:#333333;stroke:#333333;}#mermaid-svg g.stateGroup text{fill:#9370DB;stroke:none;font-size:10px;}#mermaid-svg g.stateGroup text{fill:#333;stroke:none;font-size:10px;}#mermaid-svg g.stateGroup .state-title{font-weight:bolder;fill:#131300;}#mermaid-svg g.stateGroup rect{fill:#ECECFF;stroke:#9370DB;}#mermaid-svg g.stateGroup line{stroke:#333333;stroke-width:1;}#mermaid-svg .transition{stroke:#333333;stroke-width:1;fill:none;}#mermaid-svg .stateGroup .composit{fill:white;border-bottom:1px;}#mermaid-svg .stateGroup .alt-composit{fill:#e0e0e0;border-bottom:1px;}#mermaid-svg .state-note{stroke:#aaaa33;fill:#fff5ad;}#mermaid-svg .state-note text{fill:black;stroke:none;font-size:10px;}#mermaid-svg .stateLabel .box{stroke:none;stroke-width:0;fill:#ECECFF;opacity:0.5;}#mermaid-svg .edgeLabel .label rect{fill:#ECECFF;opacity:0.5;}#mermaid-svg .edgeLabel .label text{fill:#333;}#mermaid-svg .label div .edgeLabel{color:#333;}#mermaid-svg .stateLabel text{fill:#131300;font-size:10px;font-weight:bold;}#mermaid-svg .node circle.state-start{fill:#333333;stroke:#333333;}#mermaid-svg .node .fork-join{fill:#333333;stroke:#333333;}#mermaid-svg .node circle.state-end{fill:#9370DB;stroke:white;stroke-width:1.5;}#mermaid-svg .end-state-inner{fill:white;stroke-width:1.5;}#mermaid-svg .node rect{fill:#ECECFF;stroke:#9370DB;stroke-width:1px;}#mermaid-svg .node polygon{fill:#ECECFF;stroke:#9370DB;stroke-width:1px;}#mermaid-svg #statediagram-barbEnd{fill:#333333;}#mermaid-svg .statediagram-cluster rect{fill:#ECECFF;stroke:#9370DB;stroke-width:1px;}#mermaid-svg .cluster-label,#mermaid-svg .nodeLabel{color:#131300;}#mermaid-svg .statediagram-cluster rect.outer{rx:5px;ry:5px;}#mermaid-svg .statediagram-state .divider{stroke:#9370DB;}#mermaid-svg .statediagram-state .title-state{rx:5px;ry:5px;}#mermaid-svg .statediagram-cluster.statediagram-cluster .inner{fill:white;}#mermaid-svg .statediagram-cluster.statediagram-cluster-alt .inner{fill:#f0f0f0;}#mermaid-svg .statediagram-cluster .inner{rx:0;ry:0;}#mermaid-svg .statediagram-state rect.basic{rx:5px;ry:5px;}#mermaid-svg .statediagram-state rect.divider{stroke-dasharray:10,10;fill:#f0f0f0;}#mermaid-svg .note-edge{stroke-dasharray:5;}#mermaid-svg .statediagram-note rect{fill:#fff5ad;stroke:#aaaa33;stroke-width:1px;rx:0;ry:0;}#mermaid-svg .statediagram-note rect{fill:#fff5ad;stroke:#aaaa33;stroke-width:1px;rx:0;ry:0;}#mermaid-svg .statediagram-note text{fill:black;}#mermaid-svg .statediagram-note .nodeLabel{color:black;}#mermaid-svg .statediagram .edgeLabel{color:red;}#mermaid-svg #dependencyStart,#mermaid-svg #dependencyEnd{fill:#333333;stroke:#333333;stroke-width:1;}#mermaid-svg .statediagramTitleText{text-anchor:middle;font-size:18px;fill:#333;}#mermaid-svg :root{--mermaid-font-family:"trebuchet ms",verdana,arial,sans-serif;}</style>
  <g>
    <defs>
      <marker id="mermaid-svg_statediagram-barbEnd" refX="19" refY="7" markerWidth="20" markerHeight="14" markerUnits="strokeWidth" orient="auto">
        <path d="M 19,7 L9,13 L14,7 L9,1 Z"/>
      </marker>
    </defs>
    <g class="root">
      <g class="clusters"/>
      <g class="edgePaths">
        <path d="M22,111.5L26.167,111.5C30.333,111.5,38.667,111.5,47,111.5C55.333,111.5,63.667,111.5,67.833,111.5L72,111.5" id="edge0" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M167.033,94.5L188.597,81.667C210.16,68.833,253.287,43.167,304.871,30.333C356.456,17.5,416.497,17.5,470.112,17.5C523.727,17.5,570.914,17.5,609.018,17.5C647.122,17.5,676.143,17.5,703.854,17.5C731.565,17.5,757.966,17.5,781.571,29.25C805.175,41,825.983,64.5,836.387,76.25L846.791,88" id="edge1" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M114.255,128.5L107.213,133.444C100.17,138.389,86.085,148.278,79.043,154.458C72,160.639,72,163.111,83.078,165.583C94.156,168.056,116.313,170.528,138.469,170.528C160.625,170.528,182.781,168.056,193.859,165.583C204.938,163.111,204.938,160.639,197.895,154.458C190.852,148.278,176.767,138.389,169.725,133.444L162.682,128.5" id="edge2" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M122.919,128.5L114.432,137.778C105.946,147.056,88.973,165.611,80.486,177.208C72,188.806,72,193.444,83.078,198.083C94.156,202.722,116.313,207.361,138.469,207.361C160.625,207.361,182.781,202.722,193.859,198.083C204.938,193.444,204.938,188.806,196.451,177.208C187.965,165.611,170.992,147.056,162.505,137.778L154.019,128.5" id="edge3" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M202.399,128.5L218.068,132.667C233.737,136.833,265.076,145.167,306.219,149.333C347.362,153.5,398.31,153.5,423.784,153.5L449.258,153.5" id="edge4" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M202.399,94.5L218.068,90.333C233.737,86.167,265.076,77.833,295.991,73.667C326.906,69.5,357.398,69.5,372.645,69.5L387.891,69.5" id="edge5" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M466.601,170.5L463.71,175.444C460.82,180.389,455.039,190.278,452.148,196.458C449.258,202.639,449.258,205.111,453.805,207.583C458.352,210.056,467.445,212.528,476.539,212.528C485.633,212.528,494.727,210.056,499.273,207.583C503.82,205.111,503.82,202.639,500.93,196.458C498.039,190.278,492.258,180.389,489.368,175.444L486.477,170.5" id="edge6" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M503.82,159.426L522.867,163.563C541.914,167.701,580.008,175.975,608.656,185.654C637.304,195.333,656.507,206.417,666.109,211.958L675.71,217.5" id="edge7" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M503.82,143.238L522.867,136.073C541.914,128.909,580.008,114.579,613.565,107.415C647.122,100.25,676.143,100.25,703.854,100.25C731.565,100.25,757.966,100.25,778.676,100.71C799.385,101.171,814.404,102.092,821.913,102.552L829.422,103.012" id="edge8" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M671.016,242.148L662.197,244.124C653.378,246.099,635.74,250.049,603.327,252.025C570.914,254,523.727,254,470.112,254C416.497,254,356.456,254,303.251,233.083C250.046,212.167,203.679,170.333,180.495,149.417L157.311,128.5" id="edge9" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M739.313,234.5L746.822,234.5C754.331,234.5,769.349,234.5,788.076,215.75C806.802,197,829.238,159.5,840.455,140.75L851.673,122" id="edge10" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M692.724,251.5L689.106,256.444C685.488,261.389,678.252,271.278,674.634,277.458C671.016,283.639,671.016,286.111,676.707,288.583C682.398,291.056,693.781,293.528,705.164,293.528C716.547,293.528,727.93,291.056,733.621,288.583C739.313,286.111,739.313,283.639,735.694,277.458C732.076,271.278,724.84,261.389,721.222,256.444L717.604,251.5" id="edge11" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
        <path d="M894.266,105L898.432,105C902.599,105,910.932,105,919.266,105C927.599,105,935.932,105,940.099,105L944.266,105" id="edge12" class=" edge-thickness-normal transition" style="fill:none" marker-end="url(#mermaid-svg_statediagram-barbEnd)"/>
      </g>
      <g class="edgeLabels">
        <g class="edgeLabel">
          <g class="label" transform="translate(0, 0)">
            <rect rx="0" ry="0" width="0" height="0"/>
            <foreignObject width="0" height="0">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel"/>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(618.1015625, 17.5)">
          <g class="label" transform="translate(-20.0546875, -9.5)">
            <rect rx="0" ry="0" width="40.109375" height="19"/>
            <foreignObject width="40.109375" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_eos</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(138.46875, 173)">
          <g class="label" transform="translate(-40.4140625, -9.5)">
            <rect rx="0" ry="0" width="80.828125" height="19"/>
            <foreignObject width="80.828125" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_nl</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(138.46875, 212)">
          <g class="label" transform="translate(-52.71875, -9.5)">
            <rect rx="0" ry="0" width="105.4375" height="19"/>
            <foreignObject width="105.4375" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_ws</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(296.4140625, 153.5)">
          <g class="label" transform="translate(-66.4765625, -9.5)">
            <rect rx="0" ry="0" width="132.953125" height="19"/>
            <foreignObject width="132.953125" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_keyval_key_first</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(296.4140625, 69.5)">
          <g class="label" transform="translate(-25.8828125, -9.5)">
            <rect rx="0" ry="0" width="51.765625" height="19"/>
            <foreignObject width="51.765625" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">default</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(476.5390625, 215)">
          <g class="label" transform="translate(-47.5234375, -9.5)">
            <rect rx="0" ry="0" width="95.046875" height="19"/>
            <foreignObject width="95.046875" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_keyval_key</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(618.1015625, 184.25)">
          <g class="label" transform="translate(-27.9140625, -9.5)">
            <rect rx="0" ry="0" width="55.828125" height="19"/>
            <foreignObject width="55.828125" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_equal</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(705.1640625, 100.25)">
          <g class="label" transform="translate(-20.0546875, -9.5)">
            <rect rx="0" ry="0" width="40.109375" height="19"/>
            <foreignObject width="40.109375" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_eos</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(476.5390625, 254)">
          <g class="label" transform="translate(-40.4140625, -9.5)">
            <rect rx="0" ry="0" width="80.828125" height="19"/>
            <foreignObject width="80.828125" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_nl</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(784.3671875, 234.5)">
          <g class="label" transform="translate(-20.0546875, -9.5)">
            <rect rx="0" ry="0" width="40.109375" height="19"/>
            <foreignObject width="40.109375" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">c_eos</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel" transform="translate(705.1640625, 296)">
          <g class="label" transform="translate(-25.8828125, -9.5)">
            <rect rx="0" ry="0" width="51.765625" height="19"/>
            <foreignObject width="51.765625" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel">default</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="edgeLabel">
          <g class="label" transform="translate(0, 0)">
            <rect rx="0" ry="0" width="0" height="0"/>
            <foreignObject width="0" height="0">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="edgeLabel"/>
              </div>
            </foreignObject>
          </g>
        </g>
      </g>
      <g class="nodes">
        <g class="node default" id="state-root_start-0" transform="translate(15, 111.5)">
          <circle class="state-start" r="7" width="14" height="14"/>
        </g>
        <g class="node  statediagram-state undefined" id="state-s_start-9" transform="translate(138.46875, 111.5)">
          <rect class="basic label-container" style="" x="-66.46875" y="-17" width="132.9375" height="34"/>
          <g class="label" style="" transform="translate(-58.96875, -9.5)">
            <rect/>
            <foreignObject width="117.9375" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="nodeLabel">s_start</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="node  statediagram-state undefined" id="state-s_done-12" transform="translate(861.84375, 105)">
          <rect class="basic label-container" style="" x="-32.421875" y="-17" width="64.84375" height="34"/>
          <g class="label" style="" transform="translate(-24.921875, -9.5)">
            <rect/>
            <foreignObject width="49.84375" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="nodeLabel">s_done</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="node  statediagram-state undefined" id="state-s_key-8" transform="translate(476.5390625, 153.5)">
          <rect class="basic label-container" style="" x="-27.28125" y="-17" width="54.5625" height="34"/>
          <g class="label" style="" transform="translate(-19.78125, -9.5)">
            <rect/>
            <foreignObject width="39.5625" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="nodeLabel">s_key</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="node  statediagram-state undefined" id="state-s_start_error-5" transform="translate(476.5390625, 69.5)">
          <rect class="basic label-container" style="" x="-88.6484375" y="-17" width="177.296875" height="34"/>
          <g class="label" style="" transform="translate(-81.1484375, -9.5)">
            <rect/>
            <foreignObject width="162.296875" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="nodeLabel">s_start_error</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="node  statediagram-state undefined" id="state-s_value-11" transform="translate(705.1640625, 234.5)">
          <rect class="basic label-container" style="" x="-34.1484375" y="-17" width="68.296875" height="34"/>
          <g class="label" style="" transform="translate(-26.6484375, -9.5)">
            <rect/>
            <foreignObject width="53.296875" height="19">
              <div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">
                <span class="nodeLabel">s_value</span>
              </div>
            </foreignObject>
          </g>
        </g>
        <g class="node default" id="state-root_end-12" transform="translate(951.265625, 105)">
          <circle class="state-start" r="7" width="14" height="14"/>
          <circle class="state-end" r="5" width="10" height="10"/>
        </g>
      </g>
    </g>
  </g>
  <style>@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css");</style>
</svg>
''', tmp )
    
if __name__ == '__main__':
  program_unit_test.main()
