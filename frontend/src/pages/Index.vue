<template>
  <div class='q-pa-md'>
    <div class='q-pt-md justify-evenly column'>
    <div>
      <template>
        <div class="justify-evenly row">
          <q-table
            class='table'
            table-header-class='text-primary'
            color='primary'
            dense
            table-class='text-grey-8'
            wrap-cells
            separator="cell"
            virtual-scroll
            :data="dataset_json"
            :columns="columns"
            row-key="id"
            selection="single"
            :selected.sync="selected"
            :pagination.sync="pagination"
            :selected-rows-label="getEmptyString"
            bordered
          >
            <template v-slot:top>
              <div class="text-h6 text-primary q-pl-md">Dataset</div>
              <div class='q-pl-md'>
                <q-btn-toggle
                  v-model="datasetType"
                  class="toggle"
                  no-caps
                  rounded
                  @input='resetPage()'
                  dense
                  toggle-color='primary'
                  unelevated
                  spread
                  color="white"
                  text-color="primary"
                  :options="[
                    {label: 'Exp1', value: 1},
                    {label: 'Exp2', value: 2}
                  ]"
                />
              </div>
            </template>
          </q-table>
        </div>
      </template>
    </div>
    <div class='q-pa-md justify-evenly row'>
      <div>
        <div class='row q-pb-md'>
          <q-input
          class='input-id q-pb-md'
          outlined v-model="selected[0].id"
          label="GEO ID"
          :error='!isValid'
          v-if = "showGeoInput"
          >
            <template v-slot:error>
              This id is not valid
            </template>
          </q-input>
          <div class='q-pl-md q-pt-md q-pb-md'>
            <q-btn round icon='search' color="primary" @click='searchData'/>
          </div>
          <div class='q-pl-md q-pt-md q-pb-md'>
            <q-btn :disable="disableGpt2button" round color="primary" :loading='loadGpt2' icon="send" @click='callModel'/>
          </div>
        </div>
        <q-card class="my-inputs">
          <q-card-section>
            <div class="text-h6 text-primary q-pl-md">Selected Input Data</div>
            <div class='q-pl-sm q-pr-sm' v-for="input in inputs" :key="input" >
              <q-field borderless readonly :label="input.field" stack-label>
                <template v-slot:control>
                  <div class="self-center full-width no-outline" tabindex="0">
                    <mark v-for="element in input.values" :key="element" :class="element.color">
                      {{ element.text }}
                    </mark>
                  </div>
                </template>
              </q-field>
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div>
        <div class="q-pa-md justify-evenly row">
          <div>
            <q-toggle
              class = 'q-pr-md text-grey-8'
              style="white-space: pre-wrap;"
              v-model="hideNone"
              label="Hide None:"
              @input='resetInputs()'
              left-label
            />
          </div>
          <q-btn-toggle
            v-model="typeInterpreter"
            class="toggle"
            @input="resetInputs"
            no-caps
            rounded
            unelevated
            spread
            toggle-color="primary"
            color="white"
            text-color="primary"
            :options="[
              {label: 'Gradient', value: 'gradient'},
              {label: 'Attention', value: 'attention'},
              {label: 'Lime', value: 'lime'}
            ]"
          />
        </div>
        <div class="q-pa-md">
          <q-card>
            <q-card-section>
              <div class="justify-evenly row">
                <div class="text-h6 text-primary"> Output</div>
              </div>
              <div class='my-outputs row'>
                <div class='' v-for="(output, index) in outputs" :key="output" @click="visualize(index)">
                  <div class='q-pa-sm' v-if="!((output.value === ' None' || output.value ===' unknown') && hideNone)">
                  <q-field class="output-field" label-color="grey-10" color='indigo-10' :disable="!gpt2Computed" stack-label outlined dense :bg-color='output.color' :label="output.field" >
                    <template v-slot:control>
                      <div class="self-center full-width no-outline q-pb-sm q-pt-sm text-h13" tabindex="0">{{output.value}}</div>
                    </template>

                  </q-field>
                  </div>
                </div>
                <q-dialog v-model="loadIcon" persistent transition-show="scale" transition-hide="scale">
                  <q-card style="width: 300px" class="text-primary">
                    <q-card-section>
                      <div class="text-h6">Loading</div>
                    </q-card-section>
                    <q-card-section class="q-pt-none">
                      The Lime interpreter is training, it can take a while, thank you for your patience :)
                    </q-card-section>
                    <div class='justify-evenly row q-pb-md'>
                      <q-spinner-gears color="primary" size="50px"  />
                    </div>
                  </q-card>
                </q-dialog>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
      <div class="q-pt-lg  selection-type" v-if='typeInterpreter === "attention"'>
        <q-card>
          <q-card-section>
            <div class="text-h6 text-primary">Aggregation Type</div>
            <q-option-group
              class="q-pt-md"
              v-model="aggregationType"
              :options="options"
              color="primary"
              @input='visualizeNewAggregation()'
            />
          </q-card-section>
        </q-card>
      </div>
      <div class="q-pt-lg  selection-type" v-if='!hideHeadsLayers'>
        <q-card>
          <q-card-section>
            <div class="text-h6 text-primary">Select</div>
              <div class='row justify-evenly items-center'>
                <div class="column q-pa-sm">
                  <div class='items-center column'>
                  <div class="text-h8 text-grey-9">Heads:</div>
                  <q-btn-toggle
                    v-model="headsCustomOp"
                    class="toggle"
                    @input="visualizeNewAggregation()"
                    no-caps
                    rounded
                    unelevated
                    spread
                    dense
                    toggle-color="primary"
                    color="white"
                    text-color="primary"
                    :options="[
                      {label: 'mul', value: 'mul'},
                      {label: 'avg', value: 'avg'}
                    ]"
                  />
                  </div>
                  <div class="q-pt-sm q-pl-md" v-for="(head, index) in heads_list" :key="head">
                    <q-checkbox v-model="selected_heads" :val='head' :label="index.toString()" dense color="info" @input="visualizeNewAggregation()" />
                  </div>
                </div>
                <div class="column q-pa-sm">
                  <div class="column items-center">
                  <div class="text-h8 text-grey-9">Layers:</div>
                  <q-btn-toggle
                    v-model="layersCustomOp"
                    class="toggle"
                    @input="visualizeNewAggregation()"
                    no-caps
                    rounded
                    unelevated
                    spread
                    dense
                    toggle-color="primary"
                    color="white"
                    text-color="primary"
                    :options="[
                      {label: 'mul', value: 'mul'},
                      {label: 'avg', value: 'avg'}
                    ]"
                  />
                  </div>
                  <div class="q-pt-sm q-pl-md" v-for="(layer, index) in layers_list" :key="layer" >
                    <q-checkbox v-model="selected_layers" :val='layer' :label="index.toString()" dense color="deep-purple-11" @input="visualizeNewAggregation()" />
                  </div>
                </div>
              </div>
          </q-card-section>
        </q-card>
      </div>
      </div>
    </div>
  </div>
</template>

<style lang="sass" scoped>
.selection-type
  position: relative;
  top: 60px
.table
  width: 100%
  max-height: 400px
  max-width: 65%
  min-width: 10%
.output-field
  width: 125px
  height: 95px
.my-outputs
  min-height: 150px
  max-width: 430px
  max-height: 600px
.toggle
  border: 1px solid #027be3
.input-id
  width: 40%
.my-inputs
  width: 380px
</style>

<script>
import json from '../assets/dataset.json'
import jsonTable from '../assets/dataset_table.json'
import jsonTable2 from '../assets/dataset_table2.json'
export default {
  data () {
    return {
      layersCustomOp: 'avg',
      headsCustomOp: 'avg',
      hideHeadsLayers: true,
      attentions: [],
      // http://10.79.23.5:5003 or http://localhost:5000/prova2
      backendIP: 'http://10.79.23.5',
      heads_list: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
      layers_list: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
      selected_heads: [],
      selected_layers: [],
      aggregationType: 1,
      options: [
        {
          label: 'Type 1 (last layer)',
          value: 0
        },
        {
          label: 'Type 2 (mean of layers)',
          value: 1
        },
        {
          label: 'Type 3 (multiply layers)',
          value: 2
        },
        {
          label: 'Type 4 (custom)',
          value: 3
        }
      ],
      hideNone: true,
      last_index: 'no_index',
      showGeoInput: true,
      datasetType: 1,
      typeInterpreter: 'gradient',
      disableGpt2button: true,
      loadGpt2: false,
      loadIcon: false,
      my_value: 'Submit',
      limeComputed: [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false],
      gpt2Computed: false,
      isValid: true,
      dataset: json,
      dataset_json_1: jsonTable,
      dataset_json_2: jsonTable2,
      dataset_json: jsonTable,
      selected: [{ id: '' }],
      pagination: {
        rowsPerPage: 200
      },
      columns: [
        {
          name: 'id',
          required: true,
          label: 'GEO ID',
          align: 'left',
          field: row => row.id,
          format: val => `${val}`,
          sortable: false
        },
        { name: 'title', align: 'left', label: 'TITLE', field: 'title', sortable: false },
        { name: 'description', align: 'left', label: 'DESCRIPTION', field: 'description', sortable: false },
        { name: 'characteristics', align: 'left', label: 'CHARACTERISTICS', field: 'characteristics', sortable: false }
      ],
      columns1: [
        {
          name: 'id',
          required: true,
          label: 'GEO ID',
          align: 'left',
          field: row => row.id,
          format: val => `${val}`,
          sortable: false
        },
        { name: 'title', align: 'left', label: 'TITLE', field: 'title', sortable: false },
        { name: 'description', align: 'left', label: 'DESCRIPTION', field: 'description', sortable: false },
        { name: 'characteristics', align: 'left', label: 'CHARACTERISTICS', field: 'characteristics', sortable: false }
      ],
      columns2: [
        {
          name: 'id',
          required: true,
          label: 'N°',
          align: 'left',
          field: row => row.id,
          format: val => `${val}`,
          sortable: false
        },
        { name: 'gsm', label: 'GSM', align: 'left', field: row => row.GSM, format: val => `${val}`, sortable: false },
        { name: 'gse', align: 'left', label: 'GSE', field: 'GSE', sortable: false },
        { name: 'text', align: 'left', label: 'TEXT', field: 'text', sortable: false }
      ],
      id: 'GSM1568245',
      inputs_api: [
        { field: 'Title', values: [{ text: '', color: 'bg-white' }] },
        { field: 'Description', values: [{ text: '', color: 'bg-white' }] },
        { field: 'Characteristics', values: [{ text: '', color: 'bg-white' }] }
      ],
      inputs: [
        { field: 'Title', values: [{ text: '', color: 'bg-white' }] },
        { field: 'Description', values: [{ text: '', color: 'bg-white' }] },
        { field: 'Characteristics', values: [{ text: '', color: 'bg-white' }] }
      ],
      limeResults: [[[], [], []], [[], [], []], [[], [], []], [[], [], []]],
      attentionResults: [],
      gradientResults: [],
      outputs: [],
      output_fields: {
        1: [
          'Cell Line',
          'Cell Type',
          'Tissue Type',
          'Factor'
        ],
        2: [
          'Assay name',
          'Assay type',
          'Target of assay',
          'Genome assembly',
          'Biosample term name',
          'Project',
          'Organism',
          'Life stage',
          'Age',
          'Age units',
          'Sex',
          'Ethnicity',
          'Health status',
          'Classification',
          'Investigated as'
        ]
      }
    }
  },
  name: 'PageIndex',
  methods: {
    callModel () {
      if (!this.gpt2Computed) {
        this.loadGpt2 = true
        this.$axios.post(this.backendIP + ':5003/CallModel', { inputs: this.inputs_api, output_fields: this.output_fields[this.datasetType], exp_id: this.datasetType }).then((response) => {
          this.attentions = response.data.attentions
          this.outputs = response.data.outputs
          this.gradientResults = response.data.gradient
          this.output_indexes = response.data.output_indexes
          this.$axios.post(this.backendIP + ':5003/AttentionParse', {
            inputs: this.inputs_api,
            output_fields: this.output_fields[this.datasetType],
            attentions: this.attentions,
            output_indexes: this.output_indexes,
            aggregation_type: this.aggregationType,
            selected_heads: this.selected_heads,
            selected_layers: this.selected_layers,
            headsCustomOp: this.headsCustomOp,
            layersCustomOp: this.layersCustomOp
          }).then((response) => {
            this.attentionResults = response.data.attentions_results
            this.gpt2Computed = true
            this.loadGpt2 = false
            this.disableGpt2button = true
          }).catch(error => (error.message))
        }).catch(error => (error.message))
      }
    },
    searchData () {
      this.limeComputed = [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]
      this.gpt2Computed = false
      this.id = this.selected[0].id
      if (((this.id in this.dataset) === false) && this.showGeoInput === true) {
        this.isValid = false
        this.disableGpt2button = true
        return
      }
      for (const x of Array(this.limeResults.length).keys()) {
        this.limeResults[x][0] = [{ text: '', color: 'bg-grey-3' }]
        this.limeResults[x][1] = [{ text: '', color: 'bg-grey-3' }]
        this.limeResults[x][2] = [{ text: '', color: 'bg-grey-3' }]
      }
      for (const x of Array(this.inputs.length).keys()) {
        this.inputs[x].values = [{ text: '', color: 'bg-white' }]
      }
      if (this.datasetType === 1) {
        this.inputs_api[0].values[0].text = this.dataset[this.id].title
        this.inputs_api[1].values[0].text = this.dataset[this.id].description
        this.inputs_api[2].values[0].text = this.dataset[this.id].characteristics
        this.inputs[0].values[0].text = this.dataset[this.id].title
        this.inputs[1].values[0].text = this.dataset[this.id].description
        this.inputs[2].values[0].text = this.dataset[this.id].characteristics
      }
      if (this.datasetType === 2) {
        this.inputs_api[0].values[0].text = this.dataset_json[this.id].text
        this.inputs[0].values[0].text = this.dataset_json[this.id].text
      }
      this.isValid = true
      this.disableGpt2button = false
      this.last_index = 'no_index'
    },
    visualize (index) {
      if (this.gpt2Computed) {
        if (this.typeInterpreter === 'lime') {
          if (this.limeComputed[index]) {
            for (const i of Array(this.inputs_api.length).keys()) {
              this.inputs[i].values = this.limeResults[index][i]
            }
          } else {
            this.loadIcon = true
            this.limeComputed[index] = true
            this.$axios.post(this.backendIP + ':5003/Lime', {
              inputs: this.inputs_api, outputs: this.outputs, field: this.outputs[index].field, exp_id: this.datasetType
            }).then((response) => {
              this.loadIcon = false
              for (const i of Array(this.inputs_api.length).keys()) {
                this.limeResults[index][i] = response.data[i]
                this.inputs[i].values = response.data[i]
              }
              this.loadIcon = false
            }).catch(error => (error.message))
          }
        }
        if (this.typeInterpreter === 'attention') {
          if (this.aggregationType === 3) {
            this.last_index = index
            this.visualizeNewAggregation()
          } else {
            for (const i of Array(this.inputs_api.length).keys()) {
              this.inputs[i].values = this.attentionResults[this.aggregationType][index][i]
            }
            this.last_index = index
          }
        }
        if (this.typeInterpreter === 'gradient') {
          for (const i of Array(this.inputs_api.length).keys()) {
            this.inputs[i].values = this.gradientResults[index][i]
          }
          this.last_index = index
        }
      }
    },
    resetInputs () {
      if (this.datasetType === 1) {
        this.inputs[0].values = this.inputs_api[0].values
        this.inputs[1].values = this.inputs_api[1].values
        this.inputs[2].values = this.inputs_api[2].values
      }
      if (this.datasetType === 2) {
        this.inputs[0].values = this.inputs_api[0].values
      }
    },
    getEmptyString () {
      return ''
    },
    resetPage () {
      if (this.datasetType === 1) {
        this.inputs = [
          { field: 'Title', values: [{ text: '', color: 'bg-white' }] },
          { field: 'Description', values: [{ text: '', color: 'bg-white' }] },
          { field: 'Characteristics', values: [{ text: '', color: 'bg-white' }] }
        ]

        this.inputs_api = this.inputs
        this.showGeoInput = true
        this.columns = this.columns1
        this.dataset_json = this.dataset_json_1
        this.layers_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
      }
      if (this.datasetType === 2) {
        this.inputs = [{ field: 'Text', values: [{ text: '', color: 'bg-white' }] }]
        this.inputs_api = [{ field: 'Text', values: [{ text: '', color: 'bg-white' }] }]
        this.limeResults = []
        this.layers_list = [0, 1, 2, 3, 4, 5]
        this.selected_layers = []
        for (const x of Array(this.output_fields[this.datasetType].length).keys()) {
          this.limeResults[x] = [[], [], []]
        }
        this.showGeoInput = false
        this.columns = this.columns2
        this.dataset_json = this.dataset_json_2
      }
      this.gpt2Computed = false
      this.outputs = []
      this.selected = [{ id: '' }]
      this.isValid = true
    },
    visualizeNewAggregation () {
      if (this.last_index !== 'no_index') {
        if (this.aggregationType === 3) {
          this.$axios.post(this.backendIP + ':5003/AttentionParse', {
            inputs: this.inputs_api,
            output_fields: this.output_fields[this.datasetType],
            attentions: this.attentions,
            output_indexes: this.output_indexes,
            aggregation_type: 'custom',
            selected_heads: this.selected_heads,
            selected_layers: this.selected_layers,
            headsCustomOp: this.headsCustomOp,
            layersCustomOp: this.layersCustomOp
          }).then((response) => {
            for (const i of Array(this.inputs_api.length).keys()) {
              this.inputs[i].values = response.data.attentions_results[0][this.last_index][i]
              this.attentionResults[this.aggregationType][this.last_index][i] = response.data.attentions_results[0][this.last_index][i]
            }
          }).catch(error => (error.message))
          this.hideHeadsLayers = false
        } else {
          for (const i of Array(this.inputs_api.length).keys()) {
            this.inputs[i].values = this.attentionResults[this.aggregationType][this.last_index][i]
          }
        }
      } else {
        if (this.aggregationType === 3) {
          this.hideHeadsLayers = false
        }
        for (const i of Array(this.inputs_api.length).keys()) {
          this.inputs[i].values = this.this_input_api[i].values
        }
      }
    }
  }
}
</script>
