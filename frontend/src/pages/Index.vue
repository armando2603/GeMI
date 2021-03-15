<template>
  <div class='q-pt-sm q-pb-md'>
    <div class='q-pt-md justify-evenly column'>
    <div style="width: 100%">
      <template>
        <div class="q-ml-md q-mr-md row justify-evenly">
          <q-table
            class=''
            style='max-height: 500px; max-width: 100%'
            table-header-class='text-primary'
            color='primary'
            dense
            table-class='text-grey-8'
            wrap-cells
            separator="cell"
            virtual-scroll
            :data="table_json[tableType]"
            :columns="columns"
            row-key="id"
            selection="single"
            :selected.sync="selected"
            :pagination.sync="pagination"
            :selected-rows-label="getEmptyString"
            bordered
            @update:selected ='searchData'
          >
            <template v-slot:body-cell="props">
              <q-td :props="props">
                <q-badge v-if='props.row.fields[props.col.name]' style='white-space: pre-line' :color="tableType==='corrected'?'green-4':getColorCell(props.row, props.col)" :label='props.value'/>
                <div v-if='!props.row.fields[props.col.name]'>{{props.value}}</div>
              </q-td>
            </template>
            <template v-slot:top>
              <div class="text-h6 text-primary q-pl-md">Dataset</div>
              <!-- <div class='q-pl-md'>
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
                    {label: '1', value: 1},
                    {label: '2', value: 2}
                  ]"
                />
              </div> -->
              <div class='q-pl-md'>
                <q-btn
                  rounded
                  color="primary"
                  label="Load Samples"
                  no-caps
                  @click="uploadSamples=true"
                />
                <q-dialog v-model="uploadSamples" persistent transition-show="scale" transition-hide="scale">
                  <q-card style="max-width: 95%; max-height: 100%" class="text-primary">
                    <q-card-section class='row items-center'>
                      <div class="text-h6">Load Samples</div>
                      <q-space />
                      <q-btn icon="close" @click="disableLoadSamples=true; show_error=false" flat round dense v-close-popup />
                    </q-card-section>
                    <!-- <q-card-section class="row items-start">
                      <div class='q-pr-md q-pt-sm text-grey-8'>Select dataset type :</div> -->
                      <!-- <q-btn-toggle
                        v-model="datasetType"
                        class="toggle"
                        style='width: 100px'
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
                          {label: '1', value: 1},
                          {label: '2', value: 2}
                        ]"
                      /> -->
                    <!-- </q-card-section> -->
                    <!-- <div class="row justify-start q-ml-md">
                      <div class="text-grey-8 q-mt-sm">
                        Select a Type of input :
                      </div>
                      <div class="row">
                        <q-radio v-model="GEOType" val="GSM" label="GSM" />
                        <q-radio v-model="GEOType" val="GSE" label="GSE" />
                      </div>
                    </div> -->
                    <q-card-section class="row justify-start">
                      <div class="q-mr-md q-mt-md text-grey-8">
                        {{'Insert a list of ' + 'GSES or GSMS' + ' :'}}
                      </div>
                      <div style="width: 80%">
                        <q-input outlined type='textarea' style="width:100%; max-height: 80px" v-model="GEO_list_text" stack-label placeholder="e.g GSE84422, GSM2233519..."/>
                      </div>
                    </q-card-section>
                    <div class='q-p-none q-m-none row justify-evenly'>
                      <div class="text-h6 text-red" v-if="show_error">{{error_text}}</div>
                    </div>
                    <div class='row justify-evenly'>
                      <q-btn
                        rounded
                        color="primary"
                        label="Search Samples"
                        no-caps
                        @click="searchSamples()"
                        :loading="searchingSamples"
                      />
                    </div>
                    <q-card-section class='row justify-evenly' style="max-height: 100%">
                      <template>
                        <div class="q-pa-md" style='width: 100%'>
                          <q-table
                            style="max-width: 99%; max-height: 500px"
                            table-header-class='text-primary'
                            title-class='text-primary text-h6'
                            color='primary'
                            table-class='text-grey-8'
                            wrap-cells
                            separator="cell"
                            virtual-scroll
                            row-key="GSM"
                            title="GSMS metadata"
                            :data="GSMS_data"
                            :pagination.sync="paginationGSMS"
                            :columns="GSMS_columns"
                            hide-bottom
                          />
                        </div>
                      </template>
                    </q-card-section>
                    <div class='row q-ma-md justify-evenly'>
                      <q-btn
                        rounded
                        color="primary"
                        label="Load Samples"
                        no-caps
                        :disable="GSMS_data.length === 0"
                        @click="loadSamples()"
                        :loading="loadingSamples"
                      />
                    </div>
                  </q-card>
                </q-dialog>
              </div>
              <div class='q-pl-md'>
                <q-btn
                  rounded
                  color="primary"
                  label="Export json"
                  no-caps
                  @click="exportTable"
                />
              </div>
              <div class='q-pl-md'>
                <q-btn
                  rounded
                  no-caps
                  color="primary"
                  label="Import json"
                  @click='importJSON = true'
                />
              </div>
              <q-dialog v-model="importJSON" persistent transition-show="scale" transition-hide="scale">
                <q-card style='width: 400px; height: 300px'>
                  <q-card-section class="row items-center q-pb-none">
                    <div class="text-h6 row justify-center text-primary">Import JSON</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                  </q-card-section>
                  <q-card-section class='q-pt-md row justify-evenly'>
                      <q-uploader
                        :url="backendIP + '/uploadTable'"
                        style="max-width: 300px"
                        accept=".json"
                        max-files="1"
                        hide-upload-btn
                        auto-upload
                      />
                  </q-card-section>
                  <q-card-section class='row justify-center'>
                  <q-btn
                    rounded
                    no-caps
                    color="primary"
                    label="Import"
                    @click='getJSON(); importJSON=false'
                  />
                  </q-card-section>
                </q-card>
              </q-dialog>
              <div class='q-pl-md'>
                <q-btn
                  rounded
                  color="red-4"
                  label="Delete Table"
                  no-caps
                  @click="deleteTable()"
                />
              </div>
              <q-space />
              <q-toggle
                label="Fixed GSMs"
                color="green-3"
                false-value="principal"
                true-value="corrected"
                v-model="tableType"
              />
          </template>
          </q-table>
        </div>
      </template>
    </div>
    <div class='q-pt-xl justify-evenly row'>
      <div class="q-pt-md">
        <!-- <div class='row justify-end q-pb-md'> -->
          <!-- <q-input
          class='input-id q-pb-md'
          outlined v-model="selected[0].id"
          label="GEO ID"
          :error='!isValid'
          v-if = "showGeoInput"
          >
            <template v-slot:error>
              This id is not valid
            </template>
          </q-input> -->
          <!-- <div class='q-pl-md q-pt-md q-pb-md'>
            <q-btn round icon='search' color="primary" @click='searchData'/>
          </div> -->
        <!-- </div> -->
        <q-card class="my-inputs">
          <q-card-section>
            <div class='justify-evenly row'>
              <div class="text-h6 text-primary q-pb-sm q-pl-md">Selected Input Data</div>
            </div>
            <div class='justify-evenly row' style='height: 8px'>
            <q-field class='q-pt-md' v-if='this.id !== "none"' style='height: 20px; width:55px' label-slot dense outlined readonly label-color='blue-4' stack-label>
              <template v-slot:control>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  {{id}}
                </div>
              </template>
              <template v-slot:label>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  Index
                </div>
              </template>
            </q-field>
            <q-field class='q-pt-md' v-if='this.id !== "none"' style='height: 20px; width:55px' label-slot dense outlined readonly label-color='orange-4' stack-label>
              <template v-slot:control>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  {{count_warns(table_json[tableType][id])}}
                </div>
              </template>
              <template v-slot:label>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  Warns
                </div>
              </template>
            </q-field>
            <q-field class='q-pt-md' v-if='this.id !== "none"' style='height: 20px; width: 55px' label-slot dense readonly outlined label="Fixs" label-color='green-4' stack-label>
              <template v-slot:control>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  {{count_fixs(table_json[tableType][id])}}
                </div>
              </template>
              <template v-slot:label>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  Fixes
                </div>
              </template>
            </q-field>
          </div>
          </q-card-section>
          <q-card-section>
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
      <div class='q-pt-xl q-pl-sm q-pr-sm'>
        <q-btn :disable="disableGpt2button" round color="primary" :loading='loadGpt2' icon="send" @click='callModel'/>
      </div>
      <div>
        <!-- <div class="q-pa-md justify-evenly row"> -->
          <!-- <q-btn-toggle
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
              {label: 'Attention', value: 'attention'}
            ]"
          /> -->
          <!-- <q-toggle
            class = 'q-pr-sm text-grey-8'
            style="white-space: pre-wrap;"
            v-model="hideNone"
            label="Hide None"
            @input='resetInputs()'
          /> -->
          <!-- <div class='q-pr-sm'>
          <q-btn :disable="!gpt2Computed || editcard || (last_index === 'no_index')" round color='primary' icon='rule' @click='editcard=true'/>
          </div>
        </div> -->
        <div class="q-pt-md q-pr-sm">
          <q-card style='min-width: 400px'>
            <q-card-section>
              <div class="justify-evenly row">
                <div class="text-h6 text-primary">Extracted Values</div>
                <q-btn color="primary" round icon='save' @click='checkWarns(); confirmSaveAndTrain=true' />
              </div>
              <div>
                <q-dialog v-model="confirmSaveAndTrain" persistent>
                  <q-card style="width: 350px">
                    <q-card-section>
                      <div class='justify-evenly row'>
                        <div class="text-h6 text-primary q-pb-sm q-pl-md">Save and Retrain</div>
                      </div>
                    </q-card-section>
                    <q-card-section class="row justify-evenly" v-if='loadingRegenerating || loadingRetraining'>
                      <q-spinner color="primary" size="3em" />
                    </q-card-section>
                    <q-card-section class="row justify-evenly">
                      <span v-if='!loadingRegenerating && !loadingRetraining && !missingEdit' class="q-ml-sm">You want to submit your corrections??</span>
                      <span v-if='loadingRegenerating' class="q-ml-sm">Updating the table...</span>
                      <span v-if='loadingRetraining' class="q-ml-sm">Training the model...</span>
                      <span v-if='missingEdit' class="q-ml-sm">Please edit or confirm all red and yellow values</span>
                    </q-card-section>

                    <q-card-actions v-if='!loadingRegenerating && !loadingRetraining' class="row justify-evenly">
                      <q-btn class="q-pb-sm" flat :label="missingEdit ? 'Back' : 'No'" color="primary" @click='missingEdit=false;confirmSaveAndTrain=false'/>
                      <q-btn class="q-pb-sm" v-if='!missingEdit' flat label="Yes" @click='saveAndTrain()' color="primary"/>
                    </q-card-actions>
                  </q-card>
                </q-dialog>
              </div>
              <div class='my-outputs row'>
                <div class='' v-for="(output, index) in outputs" :key="output" @click="visualize(index); editcard=true">
                  <div class='q-pa-sm' v-if="!((output.value === ' None' || output.value ===' unknown' || output.value === '<missing>') && hideNone)">
                  <q-field
                  class="output-field"
                  label-color="grey-10"
                  color='indigo-10'
                  :disable="!gpt2Computed"
                  stack-label
                  outlined
                  dense
                  :bg-color='correctionTable ? (correctionTable[index].fixed ? "info" : getOutputColor(output.confidence)) : getOutputColor(output.confidence)'
                  :label="output.field + ' [' + (correctionTable? correctionTable[index].confidence: output.confidence) + ']'" >
                    <template v-slot:control>
                      <div class="self-center full-width no-outline q-pb-sm q-pt-sm text-h13" tabindex="0">
                        {{correctionTable? (correctionTable[index].fixed ? correctionTable[index].value : output.value): output.value}}
                      </div>
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
      <div class="q-pt-md" v-if='editcard && gpt2Computed'>
        <q-card>
          <q-card-section>
            <div class="text-h6 text-primary row justify-center">Fix Output</div>
            <div class='q-pt-md'>
              <!-- <q-select
                outlined
                bg-color='grey-3'
                v-model="edit_label"
                :options="output_fields[this.datasetType]"
                label='Select field'/> -->
              <q-field borderless label="Selected Field:" label-color='primary' stack-label>
                <template v-slot:control>
                  <div class="self-center full-width no-outline" tabindex="0">
                    {{ output_fields_all[last_index] }}
                  </div>
                </template>
              </q-field>
              <q-field borderless style='width: 300px' label="Field Description:" label-color='primary' stack-label>
                <template v-slot:control>
                  <div class="self-center full-width no-outline" tabindex="0">
                    {{ descriptions[last_index] }}
                  </div>
                </template>
              </q-field>
              <q-field style='width: 300px' borderless label="Original predicted value:" label-color='primary' stack-label>
                <template v-slot:control>
                  <div class="self-center full-width no-outline" tabindex="0">
                    {{ outputs[last_index].value }}
                  </div>
                </template>
              </q-field>
              <q-field borderless label="Confidence of the predicted value:" label-color='primary' stack-label>
                <template v-slot:control>
                  <div class="self-center full-width no-outline" tabindex="0">
                    {{ outputs[last_index].confidence }}
                  </div>
                </template>
              </q-field>
              <q-field borderless style='width: 300px' label="Last edited value:" label-color='primary' stack-label>
                <template v-slot:control>
                  <div class="self-center full-width no-outline" tabindex="0">
                    {{ correctionTable ? (correctionTable[last_index].fixed ? correctionTable[last_index].value : 'Not edited') : 'Not edited' }}
                  </div>
                </template>
              </q-field>
            </div>
            <div class="text-primary q-pr-sm">
              Choose:
            </div>
            <div class="column">
              <q-radio v-model="editType" val="confirm" label="Confirm value" />
              <q-radio v-model="editType" val="unknown" label="Set as unknown" />
              <q-radio v-model="editType" val="new" label="Insert new value" />
            </div>
            <div v-if="editType==='new'" class='q-pt-md'>
              <q-input
                outlined bg-color='grey-3'
                v-model="edit_text"
                dense
                placeholder='insert new value' />
            </div>
            <div class='q-pt-md justify-evenly row'>
              <q-btn rounded size='md' color='primary' label='Edit' @click='edit()'/>
              <!-- <q-btn rounded size='sm' color='primary' label='change' @click='changeOutput()'/> -->
              <!-- <q-btn rounded size='sm' color='primary' label='confirm' @click='confirmOutput()'/> -->
            </div>
          </q-card-section>
        </q-card>
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
  max-height: 400px
  min-width: 20%
  max-width: 65%
.output-field
  width: 125px
  height: auto
.my-outputs
  min-height: 150px
  max-width: 430px
  max-height: 600px
.toggle
  min-width: 70px
  max-height: 40px
  border: 1px solid #027be3
.input-id
  width: 40%
.my-inputs
  width: 380px
</style>

<script>
// import json from '../assets/dataset.json'
// import jsonTable from '../assets/dataset_table.json'
// import jsonTable from '../assets/outputs.json'
// import jsonTable2 from '../assets/dataset_table2.json'
// import jsonTable2 from '../assets/data_pred.json'
import { exportFile } from 'quasar'

export default {
  data () {
    return {
      tableType: 'principal',
      table_json: {
        principal: [],
        corrected: []
      },
      showCorrected: false,
      missingEdit: false,
      correctionTable: undefined,
      loadingRetraining: false,
      loadingRegenerating: false,
      confirmSaveAndTrain: false,
      greenThreshold: 0.8,
      redThreshold: 0.6,
      importJSON: false,
      editType: null,
      GEOType: 'GSM',
      GSMS_data: [],
      GSMS_columns: [
        {
          name: 'GSM',
          required: true,
          label: 'GSM',
          align: 'center',
          field: row => row.GSM,
          format: val => `${val}`,
          sortable: false
        },
        { name: 'GSE', label: 'GSE', align: 'center', field: row => row.GSE, format: val => `${val}` },
        { name: 'title', label: 'title', align: 'left', field: row => row.title, format: val => `${val}` },
        { name: 'sample_type', label: 'Sample Type', align: 'left', field: row => row.sample_type, format: val => `${val}` },
        { name: 'source_name', label: 'Source Name', align: 'left', field: row => row.source_name, format: val => `${val}` },
        { name: 'organism', label: 'Organism', align: 'left', field: row => row.organism, format: val => `${val}` },
        { name: 'characteristics', label: 'Characteristics', align: 'left', field: row => row.characteristics, format: val => `${val}` },
        { name: 'description', label: 'Description', align: 'left', field: row => row.description, format: val => `${val}` }
      ],
      GEO_list_text: '',
      show_error: false,
      error_text: '',
      searchingSamples: false,
      loadingSamples: false,
      disableLoadSamples: true,
      uploadSamples: false,
      edit_text: null,
      edit_label: null,
      edit_options: [
        'Cell Line',
        'Cell Type',
        'Tissue Type',
        'Factor'
      ],
      editcard: false,
      layersCustomOp: 'avg',
      headsCustomOp: 'avg',
      hideHeadsLayers: true,
      attentions: [],
      // http://10.79.23.5:5003 or http://localhost:5003 http://2e886e4ea4d1.ngrok.io
      backendIP: 'https://341f49951322.ngrok.io',
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
        }
        // {
        //   label: 'Type 4 (custom)',
        //   value: 3
        // }
      ],
      hideNone: false,
      last_index: 'no_index',
      showGeoInput: true,
      datasetType: 2,
      typeInterpreter: 'gradient',
      disableGpt2button: true,
      loadGpt2: false,
      loadIcon: false,
      my_value: 'Submit',
      limeComputed: [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false],
      gpt2Computed: false,
      isValid: true,
      dataset_json: {
        1: [],
        2: []
      },
      selected: [{ id: null }],
      pagination: {
        rowsPerPage: 200,
        sortBy: 'warnings',
        descending: true
      },
      paginationGSMS: { rowsPerPage: 50 },
      columns: [
        {
          name: 'id',
          required: true,
          label: 'Index',
          align: 'center',
          field: row => row.id,
          format: val => `${val}`,
          sortable: true
        },
        { name: 'warnings', label: 'Warns', align: 'center', field: row => this.count_warns(row), format: val => `${val}`, sortable: true },
        { name: 'Fixs', label: 'Fixs', align: 'center', field: row => this.count_fixs(row), format: val => `${val}`, sortable: true },
        { name: 'input', align: 'left', label: 'Input', field: 'input', sortable: false, style: 'min-width: 250px' },
        { name: 'Cell Line', align: 'left', label: 'Cell Line', field: row => row.fields['Cell Line'].value, sortable: false },
        { name: 'Cell Type', align: 'left', label: 'Cell Type', field: row => row.fields['Cell Type'].value, sortable: false },
        { name: 'Tissue Type', align: 'left', label: 'Tissue Type', field: row => row.fields['Tissue Type'].value, sortable: false },
        { name: 'Factor', align: 'left', label: 'Factor', field: row => row.fields.Factor.value, sortable: false }
      ],
      columns1: [
        {
          name: 'id',
          required: true,
          label: 'Index',
          align: 'center',
          field: row => row.id,
          format: val => `${val}`,
          sortable: true
        },
        { name: 'warnings', label: 'Warns', align: 'center', field: row => this.count_warns(row), format: val => `${val}`, sortable: true },
        { name: 'Fixs', label: 'Fixs', align: 'center', field: row => this.count_fixs(row), format: val => `${val}`, sortable: true },
        { name: 'input', align: 'left', label: 'Input', field: 'input', sortable: false, style: 'min-width: 250px' },
        { name: 'Cell Line', align: 'left', label: 'Cell Line', field: row => row.fields['Cell Line'].value, sortable: false },
        { name: 'Cell Type', align: 'left', label: 'Cell Type', field: row => row.fields['Cell Type'].value, sortable: false },
        { name: 'Tissue Type', align: 'left', label: 'Tissue Type', field: row => row.fields['Tissue Type'].value, sortable: false },
        { name: 'Factor', align: 'left', label: 'Factor', field: row => row.fields.Factor.value, sortable: false }
      ],
      columns2: [
        {
          name: 'id',
          required: true,
          label: 'Index',
          align: 'center',
          field: row => row.id,
          format: val => `${val}`,
          sortable: true
        },
        { name: 'GSM', label: 'GSM', align: 'center', field: row => row.GSM, format: val => `${val}`, sortable: true },
        { name: 'GSE', label: 'GSE', align: 'center', field: row => row.GSE, format: val => `${val}`, sortable: true },
        { name: 'warnings', label: 'Warns', align: 'center', field: row => this.count_warns(row), format: val => `${val}`, sortable: true },
        { name: 'Fixs', label: 'Fixs', align: 'center', field: row => this.count_fixs(row), format: val => `${val}`, sortable: true },
        { name: 'input', align: 'left', label: 'Input', field: 'input', sortable: false, style: 'min-width: 250px' },
        { name: 'Investigated as', align: 'left', label: 'Investigated as', field: row => row.fields['Investigated as'].value, sortable: false },
        { name: 'Assay name', align: 'left', label: 'Assay name', field: row => row.fields['Assay name'].value, sortable: false },
        { name: 'Assay type', align: 'left', label: 'Assay type', field: row => row.fields['Assay type'].value, sortable: false },
        { name: 'Target of assay', align: 'left', label: 'Target of assay', field: row => row.fields['Target of assay'].value, sortable: false },
        // { name: 'Genome assembly', align: 'left', label: 'Genome assembly', field: row => row.fields['Genome assembly'].value, sortable: false },
        { name: 'Biosample term name', align: 'left', label: 'Biosample term name', field: row => row.fields['Biosample term name'].value, sortable: false },
        // { name: 'Project', align: 'left', label: 'Project', field: row => row.fields.Project.value, sortable: false },
        { name: 'Organism', align: 'left', label: 'Organism', field: row => row.fields.Organism.value, sortable: false },
        { name: 'Life stage', align: 'left', label: 'Life stage', field: row => row.fields['Life stage'].value, sortable: false },
        { name: 'Age', align: 'left', label: 'Age', field: row => row.fields.Age.value, sortable: false },
        { name: 'Age units', align: 'left', label: 'Age units', field: row => row.fields['Age units'].value, sortable: false },
        { name: 'Sex', align: 'left', label: 'Sex', field: row => row.fields.Sex.value, sortable: false },
        { name: 'Ethnicity', align: 'left', label: 'Ethnicity', field: row => row.fields.Ethnicity.value, sortable: false },
        { name: 'Health status', align: 'left', label: 'Health status', field: row => row.fields['Health status'].value, sortable: false },
        // { name: 'Classification', align: 'left', label: 'Classification', field: row => row.fields.Classification.value, sortable: false },
        { name: 'Cell Line', align: 'left', label: 'Cell Line', field: row => row.fields['Cell Line'].value, sortable: false },
        { name: 'Tissue Type', align: 'left', label: 'Tissue Type', field: row => row.fields['Tissue Type'].value, sortable: false }
      ],
      id: 'none',
      inputs_api: [
        { field: 'Input Text', values: [{ text: '', color: 'bg-white' }] }
      ],
      inputs: [
        { field: 'Input Text', values: [{ text: '', color: 'bg-white' }] }
      ],
      limeResults: [[[], [], []], [[], [], []], [[], [], []], [[], [], []]],
      attentionResults: [],
      gradientResults: [],
      outputs: [],
      output_fields_all: [
        'Investigated as',
        'Assay name',
        'Assay type',
        'Target of assay',
        'Biosample term name',
        'Organism',
        'Life stage',
        'Age',
        'Age units',
        'Sex',
        'Ethnicity',
        'Health status',
        'Cell Line',
        'Tissue Type'
      ],
      descriptions: [
        'What the target was being investigated as within an assay',
        'Type of experiment (Chip seq, rna seq, dna seq....)',
        'Super-category of experiment type',
        'For assays, such as ChIP-seq or RIP-seq, the name of the gene whose expression or product is under investigation for the experiment',
        'Name of the biosample',
        'Species of the biosample',
        'Such as “adult” or “embryonic”',
        'A string identifying the age',
        'Unit measure of the age (“month”, “year” etc.)',
        'Sex of the organism',
        'Ethnicity of the donor',
        'Brief description of the health status',
        'Cell Line',
        'Tissue Type'
      ],
      output_fields: {
        1: [
          'Cell Line',
          'Tissue Type'
        ],
        2: [
          'Investigated as',
          'Assay name',
          'Assay type',
          'Target of assay',
          'Biosample term name',
          'Organism',
          'Life stage',
          'Age',
          'Age units',
          'Sex',
          'Ethnicity',
          'Health status'
        ]
      }
    }
  },
  name: 'PageIndex',
  methods: {
    callModel () {
      if (!this.gpt2Computed) {
        this.loadGpt2 = true
        this.$axios.post(this.backendIP + '/CallModel', {
          inputs: this.inputs_api,
          output_fields: this.output_fields[this.datasetType],
          exp_id: this.datasetType,
          aggregation_type: this.aggregationType,
          selected_heads: this.selected_heads,
          selected_layers: this.selected_layers,
          headsCustomOp: this.headsCustomOp,
          layersCustomOp: this.layersCustomOp
        }).then((response) => {
          // this.attentions = response.data.attentions
          this.outputs = response.data.outputs
          this.correctionTable = JSON.parse(JSON.stringify(this.outputs))
          this.gradientResults = response.data.gradient
          // this.output_indexes = response.data.output_indexes
          // this.attentionResults = response.data.attentions_results
          this.gpt2Computed = true
          this.loadGpt2 = false
          this.disableGpt2button = true
          // this.$axios.post(this.backendIP + '/ComputeAttention', {
          //   inputs: this.inputs_api,
          //   output_fields: this.output_fields[this.datasetType],
          //   attentions: this.attentions,
          //   output_indexes: this.output_indexes,
          //   aggregation_type: this.aggregationType,
          //   selected_heads: this.selected_heads,
          //   selected_layers: this.selected_layers,
          //   headsCustomOp: this.headsCustomOp,
          //   layersCustomOp: this.layersCustomOp
          // }).then((response) => {
          //   this.attentionResults = response.data.attentions_results
          //   this.gpt2Computed = true
          //   this.loadGpt2 = false
          //   this.disableGpt2button = true
          // }).catch(error => (error.message))
        }).catch(error => {
          console.log(error)
          this.loadGpt2 = false
        })
      }
    },
    searchData (newSelected) {
      this.limeComputed = [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]
      this.gpt2Computed = false
      this.editcard = false
      this.id = this.selected[0].id

      for (const x of Array(this.limeResults.length).keys()) {
        this.limeResults[x][0] = [{ text: '', color: 'bg-grey-3' }]
      }
      for (const x of Array(this.inputs.length).keys()) {
        this.inputs[x].values = [{ text: '', color: 'bg-white' }]
      }
      if (this.datasetType === 1) {
        this.inputs_api[0].values[0].text = this.table_json[this.tableType][this.id].input
        this.inputs[0].values[0].text = this.table_json[this.tableType][this.id].input
      }
      if (this.datasetType === 2) {
        this.inputs_api[0].values[0].text = this.table_json[this.tableType][this.id].input
        this.inputs[0].values[0].text = this.table_json[this.tableType][this.id].input
      }
      this.isValid = true
      this.disableGpt2button = false
      this.last_index = 'no_index'
    },
    visualize (index) {
      this.edit_text = ''
      if (this.gpt2Computed) {
        if (this.typeInterpreter === 'lime') {
          if (this.limeComputed[index]) {
            for (const i of Array(this.inputs_api.length).keys()) {
              this.inputs[i].values = this.limeResults[index][i]
            }
          } else {
            this.loadIcon = true
            this.limeComputed[index] = true
            this.$axios.post(this.backendIP + '/Lime', {
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
      this.edit_text = null
      this.edit_label = null
      this.id = 'none'
      this.inputs = [{ field: 'Text', values: [{ text: '', color: 'bg-white' }] }]
      this.inputs_api = [{ field: 'Text', values: [{ text: '', color: 'bg-white' }] }]
      if (this.datasetType === 1) {
        this.showGeoInput = true
        this.columns = this.columns1
        this.layers_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
      }
      if (this.datasetType === 2) {
        this.limeResults = []
        // this.layers_list = [0, 1, 2, 3, 4, 5]
        this.selected_layers = []
        for (const x of Array(this.output_fields[this.datasetType].length).keys()) {
          this.limeResults[x] = [[], [], []]
        }
        this.showGeoInput = false
        this.columns = this.columns2
      }
      this.gpt2Computed = false
      this.outputs = []
      this.selected = [{ id: null }]
      this.isValid = true
      this.tableType = 'principal'
    },
    // visualizeNewAggregation () {
    //   if (this.last_index !== 'no_index') {
    //     if (this.aggregationType === 3) {
    //       this.$axios.post(this.backendIP + '/ComputeAttention', {
    //         inputs: this.inputs_api,
    //         output_fields: this.output_fields[this.datasetType],
    //         attentions: this.attentions,
    //         output_indexes: this.output_indexes,
    //         aggregation_type: 'custom',
    //         selected_heads: this.selected_heads,
    //         selected_layers: this.selected_layers,
    //         headsCustomOp: this.headsCustomOp,
    //         layersCustomOp: this.layersCustomOp
    //       }).then((response) => {
    //         for (const i of Array(this.inputs_api.length).keys()) {
    //           this.inputs[i].values = response.data.attentions_results[0][this.last_index][i]
    //           this.attentionResults[this.aggregationType][this.last_index][i] = response.data.attentions_results[0][this.last_index][i]
    //         }
    //       }).catch(error => (error.message))
    //       this.hideHeadsLayers = false
    //     } else {
    //       this.hideHeadsLayers = true
    //       for (const i of Array(this.inputs_api.length).keys()) {
    //         this.inputs[i].values = this.attentionResults[this.aggregationType][this.last_index][i]
    //       }
    //     }
    //   } else {
    //     if (this.aggregationType === 3) {
    //       this.hideHeadsLayers = false
    //     } else {
    //       this.hideHeadsLayers = true
    //     }
    //     for (const i of Array(this.inputs_api.length).keys()) {
    //       this.inputs[i].values = this.this_input_api[i].values
    //     }
    //   }
    // },
    count_warns (row) {
      var nWarn = 0
      for (var field of this.output_fields[this.datasetType]) {
        if (row.fields[field].confidence <= this.redThreshold) {
          nWarn += 1
        }
      }
      return nWarn
    },
    count_fixs (row) {
      var nFix = 0
      for (var field of this.output_fields[this.datasetType]) {
        if (row.fields[field].fixed === true) {
          nFix += 1
        }
      }
      return nFix
    },
    store_json () {
      this.$axios.post(
        this.backendIP + '/storeJSON',
        { table: this.table_json[this.tableType], table_id: this.datasetType }
      ).catch(error => (error.message))
    },
    changeOutput () {
      // this.dataset_json[this.datasetType][this.id].fields[this.output_fields[this.datasetType][this.last_index]].value = this.edit_text
      // this.dataset_json[this.datasetType][this.id].fields[this.output_fields[this.datasetType][this.last_index]].confidence = 1
      // this.dataset_json[this.datasetType][this.id].fields[this.output_fields[this.datasetType][this.last_index]].fixed = true
      // this.store_json()
      this.correctionTable[this.last_index].confidence = 1
      this.correctionTable[this.last_index].fixed = true
      this.correctionTable[this.last_index].value = this.edit_text
    },
    confirmOutput () {
      // this.dataset_json[this.datasetType][this.id].fields[this.output_fields[this.datasetType][this.last_index]].confidence = 1
      // this.dataset_json[this.datasetType][this.id].fields[this.output_fields[this.datasetType][this.last_index]].fixed = true
      // this.store_json()
      this.correctionTable[this.last_index].confidence = 1
      this.correctionTable[this.last_index].fixed = true
    },
    exportTable () {
      const status = exportFile(
        'table-export.json',
        JSON.stringify(this.table_json[this.tableType]),
        'text/json'
      )

      if (status !== true) {
        this.$q.notify({
          message: 'Browser denied file download...',
          color: 'negative',
          icon: 'warning'
        })
      }
    },
    loadSamples () {
      this.loadingSamples = true
      this.$axios.post(
        this.backendIP + '/generateTable',
        { output_fields: this.output_fields[2], exp_id: 2, data: this.GSMS_data }
      ).then(response => {
        this.$axios.get(this.backendIP + '/getJSONs')
          .then((response) => {
            // this.dataset_json[1] = response.data[0]
            this.table_json[this.tableType] = response.data[1]
            this.loadingSamples = false
            this.uploadSamples = false
            this.show_error = false
          }).catch(error => (error.message))
      }).catch(error => {
        this.loadingSamples = false
        this.disableLoadSamples = true
        this.show_error = true
        console.log(error)
        this.error_text = 'Something went wrong with the loading'
      })
    },
    searchSamples () {
      if (this.GEO_list_text.trim() === '') {
        this.GSMS_data = []
        return
      }
      this.show_error = false
      this.searchingSamples = true
      const searchList = this.GEO_list_text.trim().replace('"', '').replace("'", '').split(',').map(elem => elem.trim().toUpperCase())
      console.log(searchList)
      this.$axios.post(
        this.backendIP + '/searchGEO',
        { searchList: searchList }
      ).then(response => {
        this.GSMS_data = response.data
        this.searchingSamples = false
      }).catch(error => {
        console.log(error.message)
        this.searchingSamples = false
        this.show_error = true
        this.error_text = 'Something went wrong, please control the input'
      })
    },
    deleteTable () {
      this.$axios.post(
        this.backendIP + '/deleteTable',
        { table_id: this.datasetType }
      ).catch(error => {
        console.log(error.message)
      })
      for (const tableType in this.table_json) this.table_json[tableType] = []
      this.resetPage()
    },
    edit () {
      this.$axios.post(
        this.backendIP + '/writeLog',
        {
          editType: this.editType,
          GSM: this.table_json[this.tableType][this.id].GSM,
          input_text: this.table_json[this.tableType][this.id].input,
          edit_text: this.edit_text,
          prediction: this.outputs[this.last_index].value,
          field: this.outputs[this.last_index].field
        }
      ).catch(error => (error.message))
      if (this.editType === 'confirm') {
        this.confirmOutput()
      }
      if (this.editType === 'unknown') {
        this.edit_text = 'unknown'
        this.changeOutput()
        this.edit_text = ''
      }
      if (this.editType === 'new') {
        this.changeOutput()
      }
      for (const newIndex in this.correctionTable) {
        if (this.correctionTable[newIndex].confidence <= this.greenThreshold) {
          this.last_index = newIndex
          this.visualize(newIndex)
          break
        }
      }
    },
    getJSON () {
      this.$axios.get(this.backendIP + '/getJSONs')
        .then((response) => {
          this.dataset_json[1] = response.data[0]
          this.table_json[this.tableType] = response.data[1]
        }).catch(error => (error.message))
    },
    getColorCell (row, col) {
      if (this.table_json[this.tableType] !== []) {
        if (this.table_json[this.tableType] !== []) {
          const field = this.table_json[this.tableType][row.id].fields[col.name]
          if (field !== undefined) {
            const confidence = field.confidence
            if (field.fixed) return 'info'
            if (confidence > this.greenThreshold) return 'green-4'
            if (confidence < this.redThreshold) {
              return 'red-4'
            } else {
              return 'orange-4'
            }
          }
        }
      }
      return ''
    },
    saveAndTrain () {
      this.loadingRetraining = true
      const outputText = { 1: '', 2: '' }
      let tableType
      for (const [index, output] of this.correctionTable.entries()) {
        if (index < this.correctionTable.length - 2) tableType = 2
        else tableType = 1
        outputText[tableType] += output.field + ': ' + output.value
        // console.log(this.correctionTable[index].field)
        // console.log(this.output_fields[tableType].slice(-1))
        if (output.field === this.output_fields[tableType].slice(-1)[0]) {
          outputText[tableType] += '<EOS>'
        } else {
          outputText[tableType] += '<SEPO>'
        }
      }
      // console.log(this.output_fields[2].slice(-1))
      console.log(outputText)
      this.$axios.post(
        this.backendIP + '/saveAndTrain',
        {
          input_text: this.table_json[this.tableType][this.id].input,
          output_text: outputText
        }
      ).then((response) => {
        const inputList = []
        for (const row of this.table_json[this.tableType]) {
          inputList.push({
            input_text: row.input,
            GSE: row.GSE,
            GSM: row.GSM
          })
        }
        for (const [index, field] of this.output_fields_all.entries()) {
          this.table_json[this.tableType][this.id].fields[field].value = this.correctionTable[index].value
          this.table_json[this.tableType][this.id].fields[field].confidence = this.correctionTable[index].confidence
          this.table_json[this.tableType][this.id].fields[field].fixed = this.correctionTable[index].fixed
        }
        this.loadingRetraining = false
        this.loadingRegenerating = true
        this.$axios.post(
          this.backendIP + '/regenerateTable',
          {
            inputList: inputList,
            output_fields: this.output_fields[2],
            exp_id: 2
          }
        ).then((response) => {
          // this.dataset_json[this.datasetType] = response.data
          const newTable = response.data
          for (const [index, row] of this.table_json[this.tableType].entries()) {
            for (const field of this.output_fields_all) {
              if (this.table_json[this.tableType][index].fields[field].fixed) {
                // console.log('uno fixato')
                // console.log(row.fields[field].value)
                newTable[index].fields[field].value = row.fields[field].value
                newTable[index].fields[field].confidence = row.fields[field].confidence
                newTable[index].fields[field].fixed = true
              }
            }
            this.loadingRegenerating = false
          }
          const correctedRow = JSON.parse(JSON.stringify(this.table_json[this.tableType][this.id]))
          correctedRow.id = this.table_json.corrected.length
          this.table_json.corrected.push(correctedRow)
          const filteredTable = []
          for (const row of newTable) {
            if (row.id !== this.id) {
              if (row.id > this.id) row.id = row.id - 1
              filteredTable.push(row)
            }
          }
          this.table_json[this.tableType] = filteredTable
          console.log('dovrebbe aver salvato')
          this.store_json()
          this.confirmSaveAndTrain = false
          this.resetPage()
        }).catch(error => {
          console.log(error.message)
          this.confirmSaveAndTrain = false
        })
      }).catch(error => {
        console.log(error.message)
        this.loadingRetraining = false
      })
    },
    getOutputColor (confidence) {
      if (confidence > this.greenThreshold) return 'green-3'
      else {
        if (confidence < this.redThreshold) return 'red-3'
        else return 'orange-3'
      }
    },
    checkWarns () {
      for (const index in this.correctionTable) {
        if (this.correctionTable[index].confidence <= this.greenThreshold) this.missingEdit = true
      }
    }
  },
  created () {
    this.columns = this.columns2
    this.$axios.get(this.backendIP + '/getJSONs')
      .then((response) => {
        this.dataset_json[1] = response.data[0]
        this.table_json[this.tableType] = response.data[1]
        this.resetPage()
      }).catch(error => (error.message))
  }
}
</script>
