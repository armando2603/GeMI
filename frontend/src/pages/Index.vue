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
          <div class='q-pl-md q-pt-sm'>
            <q-btn round icon='search' color="primary" @click='searchData'/>
          </div>
          <div class='q-pl-md q-pt-sm'>
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
                <div class='q-pa-sm' v-for="(output, index) in outputs" :key="output" @click="visualize(index)">
                  <q-field class="output-field" label-color="grey-10" :disable="!gpt2Computed" stack-label outlined :bg-color='output.color' :label="output.field" >
                    <template v-slot:control>
                      <div class="self-center full-width no-outline" tabindex="0">{{output.value}}</div>
                    </template>
                  </q-field>
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
      </div>
    </div>
  </div>
</template>

<style lang="sass" scoped>
.table
  width: 100%
  max-height: 400px
  max-width: 65%
  min-width: 10%
.output-field
  width: 120px
  height: 60px
.my-outputs
  min-height: 150px
  max-width: 410px
  max-height: 500px
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
      showGeoInput: true,
      datasetType: 1,
      typeInterpreter: 'attention',
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
      attentionResults: [[[], [], []], [[], [], []], [[], [], []], [[], [], []]],
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
        // http://10.79.23.5:5003 or http://localhost:5000/prova2
        this.$axios.post('http://10.79.23.5:5003/prova2', { inputs: this.inputs_api, output_fields: this.output_fields[this.datasetType], exp_id: this.datasetType }).then((response) => {
          this.outputs = response.data.outputs
          this.attentionResults = response.data.attentions
          this.gpt2Computed = true
          this.loadGpt2 = false
          this.disableGpt2button = true
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
            this.$axios.post('http://10.79.23.5:5003/prova', {
              inputs: this.inputs_api, outputs: this.outputs, field: this.outputs[index].field
            }).then((response) => {
              for (const i of Array(this.inputs_api.length).keys()) {
                this.limeResults[index][i] = response.data[i]
                this.inputs[i].values = response.data[i]
              }
              this.loadIcon = false
            }).catch(error => (error.message))
          }
        }
        if (this.typeInterpreter === 'attention') {
          for (const i of Array(this.inputs_api.length).keys()) {
            this.inputs[i].values = this.attentionResults[index][i]
          }
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
      }
      if (this.datasetType === 2) {
        this.inputs = [{ field: 'Text', values: [{ text: '', color: 'bg-white' }] }]
        this.inputs_api = this.inputs
        this.showGeoInput = false
        this.columns = this.columns2
        this.dataset_json = this.dataset_json_2
      }
      this.gpt2Computed = false
      this.outputs = []
      this.selected = [{ id: '' }]
      this.isValid = true
    }
  }
}
</script>
