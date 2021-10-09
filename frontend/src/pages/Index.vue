<template>
  <div class='q-pt-sm q-pb-md'>
    <q-dialog v-model='showInstructions'>
      <q-card class="row items-center" style='min-width: 55%'>
        <q-card-section class='row' style='width: 100%'>
          <div class="q-pl-xl text-h6 text-primary col-11"><a>Tutorial</a></div>
          <div class='col-1 row justify-end'>
          <q-btn class='' icon="close" color='primary' flat round dense v-close-popup />
          </div>
        </q-card-section>
        <q-card-section class='q-pa-xl' style='width:100%'>
          <!-- <div class="text-h4 q-pb-sm row justify-evenly text-primary"><span>Tutorial</span></div> -->
          <div class='q-pa-md' style='width:100%'>
            <q-video class='q-pa-md' :ratio='14/7' style='width:100%' src="https://www.youtube.com/embed/HLcDDIQ69YA"/>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
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
                    <q-card-section class='row'>
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
                        Select input type :
                      </div>
                      <div class="row">
                        <q-radio v-model="searchType" val="input" label="input text" />
                        <q-radio v-model="searchType" val="upload" label="upload file" />
                      </div>
                    </div> -->
                    <q-card-section>
                      <div class='row justify-evenly'>
                        <div style='width: 80%' class="q-mb-md q-pb-sm q-mt-sm row justify-evenly text-grey-8">
                          <div style='text-align: center'>
                            <a>Provide a comma separate list of GSEs/GSMs uploading a file or using the form below. </a>
                            <a>To find geo ids you can use the following links: </a><a target="_blank" class="" href='https://www.ncbi.nlm.nih.gov/sites/GDSbrowser'>GEO dataset browser</a><a> or </a><a target="_blank" href='http://stargeo.org/search/'>stargeo</a>
                          </div>
                        </div>
                      </div>
                      <div class="row justify-center">
                      <q-file style="width:240px" accept='.text, .txt' label='Upload a text file' filled bottom-slots v-model="fileGEO" @input='loadText()'  counter>
                        <template v-slot:prepend>
                          <q-icon name="cloud_upload" />
                        </template>
                        <template v-slot:append>
                          <q-icon name="close" @click="fileGEO = null" class="cursor-pointer" />
                        </template>
                      </q-file>
                      </div>
                      <div class="q-mr-md q-mt-md text-grey-8">
                        {{'List of ' + 'GSEs or GSMs' + ' :'}}
                      </div>
                      <div style="width: 95%">
                        <q-input outlined type='textarea' style="width:100%; max-height: 100px" v-model="GEO_list_text" stack-label placeholder="e.g GSE84422, GSM2233519..."/>
                      </div>
                    </q-card-section>
                    <div class='q-p-none q-m-none row justify-evenly'>
                      <div class="text-h6 text-red" v-if="show_error">{{error_text}}</div>
                    </div>
                    <div class='row justify-evenly'>
                      <q-btn
                        rounded
                        color="primary"
                        label="Download Samples"
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
                            title="Samples Metadata"
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
                        :percentage='loadStatus'
                      >
                        <template v-slot:loading>
                          {{loadStatus}} %
                        </template>
                      </q-btn>
                    </div>
                  </q-card>
                </q-dialog>
              </div>
              <div class='q-pl-md'>
                <q-btn
                  rounded
                  color="primary"
                  label="Export JSON"
                  no-caps
                  @click="exportTable"
                />
              </div>
              <!-- <div class='q-pl-md'>
                <q-btn
                  rounded
                  color="primary"
                  label="Export CSV"
                  no-caps
                  @click="exportCSV"
                />
              </div> -->
              <!-- <div class='q-pl-md'>
                <q-btn
                  rounded
                  no-caps
                  color="primary"
                  label="Import Table"
                  @click='importJSON = true'
                /> -->
              <!-- </div> -->
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
              <q-btn
                rounded
                color="green-4"
                label="Save All"
                no-caps
                v-if='getSampleWithMaxWarns().id !== null && getSampleWithMaxWarns().max === 0'
                @click="moveAll()"
              />
              <q-toggle
                label="Saved Samples"
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
              <div class="text-h6 text-primary">Selected Sample Data</div>
            </div>
            <div class='justify-evenly row' style='height: 8px'>
            <q-field class='q-pt-md' v-if='this.id !== "none"' style='height: 20px; width:90px' label-slot dense outlined readonly label-color='blue-4' stack-label>
              <template v-slot:control>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  {{id}}
                </div>
              </template>
              <template v-slot:label>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  Sample Index
                </div>
              </template>
            </q-field>
            <!-- <q-field class='q-pt-md' v-if='this.id !== "none"' style='height: 20px; width:55px' label-slot dense outlined readonly label-color='red-4' stack-label>
              <template v-slot:control>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  {{count_warns(table_json[tableType][id])}}
                </div>
              </template>
              <template v-slot:label>
                <div class="self-center full-width no-outline" style='text-align: center' tabindex="0">
                  Critics
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
            </q-field> -->
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
      <!-- <div class='q-pt-xl q-pl-sm q-pr-sm'>
        <q-btn :disable="disableGpt2button" round color="primary" :loading='loadGpt2' icon="send" @click='callModel'/>
      </div> -->
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
                <div class="text-h6 text-primary">Extracted Fields</div>
              </div>
              <div>
                <q-dialog v-model="confirmSaveAndTrain" persistent>
                  <q-card style="width: 350px">
                    <q-card-section>
                      <div class='justify-evenly row'>
                        <div class="text-h6 text-primary q-pb-sm q-pl-md">Save and Retrain</div>
                      </div>
                    </q-card-section>
                    <q-card-section class="row justify-evenly" v-if='loadingRetraining'>
                      <q-spinner color="primary" size="3em" />
                    </q-card-section>
                    <q-card-section class="row justify-evenly" v-if='loadingRegenerating'>
                      <q-circular-progress
                        show-value
                        class=""
                        :value="loadStatus"
                        size="5em"
                        font-size="16px"
                        color="primary"
                      >
                      {{ loadStatus }}%
                      </q-circular-progress>
                    </q-card-section>
                    <q-card-section class="row justify-evenly">
                      <span v-if='!loadingRegenerating && !loadingRetraining && !zeroWarns' class="q-ml-sm">You want to submit your corrections??</span>
                      <span v-if='loadingRegenerating' class="q-ml-sm">Updating the table...</span>
                      <span v-if='loadingRetraining' class="q-ml-sm">Training the model...</span>
                      <!-- <span v-if='missingEdit' class="q-ml-sm">Please edit or confirm all red and yellow values</span> -->
                      <span v-if='zeroWarns' class="q-ml-sm" style='text-align: center'>There are no more critical samples, now you can inspect the remaining samples and save all the remaining samples  with the 'Save All' button. Once all samples are saved you can download them with the 'Export' button  </span>
                    </q-card-section>

                    <q-card-actions v-if='!loadingRegenerating && !loadingRetraining' class="row justify-evenly">
                      <q-btn class="q-pb-sm" flat :label="(zeroWarns) ? 'Back' : 'No'" color="primary" @click='missingEdit=false;confirmSaveAndTrain=false; zeroWarns=false'/>
                      <q-btn class="q-pb-sm" v-if='!zeroWarns' flat label="Yes" @click='saveAndTrain()' color="primary"/>
                    </q-card-actions>
                  </q-card>
                </q-dialog>
              </div>
              <div v-if='loadGpt2' class='row q-mt-md q-mb-md justify-evenly'>
                <q-spinner color="primary" size="4em" />
              </div>
              <div v-if='!loadGpt2' class='my-outputs row'>
                <div ref='outputField' class='' v-for="(output, index) in outputs" :key="output" @click="visualize(index); editcard=true">
                  <div class='q-pa-sm' v-if="!((output.value === ' None' || output.value ===' unknown' || output.value === '<missing>') && hideNone)">
                  <q-field
                  :class="index===last_index?'output-field q-field--focused':'output-field'"
                  label-color="grey-10"
                  color='indigo-8'
                  :disable="!gpt2Computed"
                  stack-label
                  outlined
                  dense
                  :bg-color='correctionTable ? (correctionTable[index].fixed ? "info" : getOutputColor(output.confidence)) : getOutputColor(output.confidence)'
                  :label="output_fields_names[index] + ' [' + Math.round((correctionTable? correctionTable[index].confidence: output.confidence) * 100) + '%]'" >
                    <template v-slot:control>
                      <div class="self-center full-width no-outline q-pb-sm q-pt-md text-h13" tabindex="0">
                        {{correctionTable? (correctionTable[index].fixed ? correctionTable[index].value : output.value): output.value}}
                      </div>
                    </template>
                    <!-- <template class='' v-slot:label>
                      <div class="q-pt-sm row items-start" style='white-space: normal'>
                        <span>
                          {{output.field + ' [' + (correctionTable? correctionTable[index].confidence: output.confidence) * 100 + '%]'}}
                        </span>
                      </div>
                    </template> -->
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
              <div class="row justify-center">
                <q-btn class='q-mt-sm' color="primary" no-caps rounded label='Save Sample' :disabled='!checkAtLeastOneCorrection()' v-if='tableType==="principal" && !loadGpt2 && gpt2Computed' @click='checkWarns(); confirmSaveAndTrain=true' />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
      <!-- <div class="q-pt-md" v-if='editcard && gpt2Computed'> -->
      <div class="q-pt-md">
        <q-card style="min-width: 320px;min-height: 150px">
          <q-card-section>
            <div class="text-h6 text-primary row justify-center">Edit Form</div>
            <div class='' v-if='!loadGpt2 && gpt2Computed'>
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
                      {{ last_index === 'no_index' ? 'Select a field' : output_fields_names[last_index] }}
                    </div>
                  </template>
                </q-field>
                <q-field borderless style='width: 300px' label="Field Description:" label-color='primary' stack-label>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">
                      {{ last_index === 'no_index' ? 'Select a field' : descriptions[last_index] }}
                      <a v-if='[5,6,7,8,9,10, 13].includes(last_index)'>in this case check the value on </a>
                      <a v-if='[5,6,7,8,9,10, 13].includes(last_index)' href='https://www.lgcstandards-atcc.org/search#sort=relevancy' target="_blank">ATCC</a>
                      <a v-if='[5,6,7,8,9,10, 13].includes(last_index)'> or </a>
                      <a v-if='[5,6,7,8,9,10, 13].includes(last_index)' href='https://web.expasy.org/cellosaurus/' target="_blank">Expasy Cellosaurus</a>
                      <a v-if='[5,6,7,8,9].includes(last_index)'> )</a>
                    </div>
                  </template>
                </q-field>
                <q-field borderless style='width: 300px' label="Most common values:" label-color='primary' stack-label>
                  <template v-slot:control>
                    <div class='row'>
                      <div class="q-pr-sm" v-for="(values, index) in output_fields_common_values[last_index].values" :key="values">
                        <a target="_blank" :href="output_fields_common_values[last_index].links[index]">{{values}}</a>
                      </div>
                    </div>
                  </template>
                </q-field>
                <q-field style='width: 300px' borderless label="Original predicted value:" label-color='primary' stack-label>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">
                      {{ last_index === 'no_index' ? 'Select a field' : outputs[last_index].value }}
                    </div>
                  </template>
                </q-field>
                <q-field borderless label="Confidence of the predicted value:" label-color='primary' stack-label>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">
                      {{ last_index === 'no_index' ? 'Select a field' : Math.round(outputs[last_index].confidence *100) + '%' }}
                    </div>
                  </template>
                </q-field>
                <q-field borderless style='width: 300px' label="Edited value:" label-color='primary' stack-label>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">
                      {{ last_index === 'no_index' ? 'Select a field' : (correctionTable ? (correctionTable[last_index].fixed ? correctionTable[last_index].value : 'Not edited') : 'Not edited') }}
                    </div>
                  </template>
                </q-field>
              </div>
              <div class="text-primary row justify-evenly q-pr-sm">
                  Choose:
                </div>
              <div class='row justify-evenly'>
                <div class="column">
                <q-radio v-model="editType" val="confirm" label="Confirm value" />
                <q-radio v-model="editType" val="unknown" label="Set as unknown" />
                <q-radio v-model="editType" val="new" label="Insert new value" />
              </div>
              </div>
              <div v-if="editType==='new'" class='q-pt-md'>
                <!-- <q-input
                  outlined bg-color='grey-3'
                  v-model="edit_text"
                  dense
                  placeholder='insert new value' /> -->
                <q-select
                  outlined
                  dense
                  bg-color='grey-3'
                  v-model="edit_text"
                  use-input
                  fill-input
                  hide-selected
                  @input-value="onInputValue"
                  input-debounce="0"
                  :options="filterOptions"
                  new-value-mode="add-unique"
                  @filter="filterFn"
                  @click.capture.native="onClick"
                  @popup-hide="onPopupHide"
                  @popup-show="onPopupShow"
                />
              </div>
              <div class='q-pt-md justify-evenly row'>
                <q-btn rounded size='md' color='primary' no-caps label='Apply' @click='edit()'/>
                <!-- <q-btn rounded size='sm' color='primary' label='change' @click='changeOutput()'/> -->
                <!-- <q-btn rounded size='sm' color='primary' label='confirm' @click='confirmOutput()'/> -->
              </div>
            </div>
            <div v-if='loadGpt2' class='row q-mt-md q-mb-md justify-evenly'>
              <q-spinner color="primary" size="4em" />
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
  width: 133px
  height: auto
.my-outputs
  min-height: 150px
  max-width: 450px
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
import fieldsValues from '../assets/fields_values.json'
// import jsonTable from '../assets/dataset_table.json'
// import jsonTable from '../assets/outputs.json'
// import jsonTable2 from '../assets/dataset_table2.json'
// import jsonTable2 from '../assets/data_pred.json'
import { exportFile } from 'quasar'

export default {
  data () {
    return {
      inputIndexes: [],
      popupOpen: false,
      filterOptions: [],
      stringOptions: fieldsValues,
      loadStatus: 0,
      showInstructions: true,
      InstructionSlide: 'loading samples',
      zeroWarns: false,
      fileGEO: null,
      searchType: 'input',
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
      editType: 'confirm',
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
      backendIP: 'http://localhost:51113',
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
        { name: 'warnings', label: 'Criticals', align: 'center', field: row => this.count_warns(row), format: val => `${val}`, sortable: true },
        // { name: 'Fixs', label: 'Fixs', align: 'center', field: row => this.count_fixs(row), format: val => `${val}`, sortable: true },
        { name: 'input', align: 'left', label: 'Sample text', field: 'input', sortable: false, style: 'min-width: 250px' },
        { name: 'Investigated as', align: 'left', label: 'Feature', field: row => row.fields['Investigated as'].value, sortable: true },
        { name: 'Assay name', align: 'left', label: 'Techinique', field: row => row.fields['Assay name'].value, sortable: true },
        { name: 'Assay type', align: 'left', label: 'Technique Type', field: row => row.fields['Assay type'].value, sortable: true },
        { name: 'Target of assay', align: 'left', label: 'Target', field: row => row.fields['Target of assay'].value, sortable: true },
        // { name: 'Genome assembly', align: 'left', label: 'Genome assembly', field: row => row.fields['Genome assembly'].value, sortable: true },
        // { name: 'Biosample term name', align: 'left', label: 'Biosample', field: row => row.fields['Biosample term name'].value, sortable: true },
        // { name: 'Project', align: 'left', label: 'Project', field: row => row.fields.Project.value, sortable: true },
        { name: 'Organism', align: 'left', label: 'Species', field: row => row.fields.Organism.value, sortable: true },
        { name: 'Life stage', align: 'left', label: 'Life stage', field: row => row.fields['Life stage'].value, sortable: true },
        { name: 'Age', align: 'left', label: 'Age', field: row => row.fields.Age.value, sortable: true },
        { name: 'Age units', align: 'left', label: 'Age units', field: row => row.fields['Age units'].value, sortable: true },
        { name: 'Sex', align: 'left', label: 'Sex', field: row => row.fields.Sex.value, sortable: true },
        { name: 'Ethnicity', align: 'left', label: 'Ethnicity', field: row => row.fields.Ethnicity.value, sortable: true },
        { name: 'Health status', align: 'left', label: 'Disease', field: row => row.fields['Health status'].value, sortable: true },
        { name: 'Cell Line', align: 'left', label: 'Cell Line', field: row => row.fields['Cell Line'].value, sortable: true },
        { name: 'Cell Type', align: 'left', label: 'Cell Type', field: row => row.fields['Cell Type'].value, sortable: true },
        { name: 'Tissue Type', align: 'left', label: 'Tissue', field: row => row.fields['Tissue Type'].value, sortable: true }
        // { name: 'Classification', align: 'left', label: 'Biosample Type', field: row => row.fields.Classification.value, sortable: true }
      ],
      id: 'none',
      inputs_api: [
        { field: 'gse:', values: [{ text: '', color: 'bg-white' }] }
      ],
      inputs: [
        { field: 'gse:', values: [{ text: '', color: 'bg-white' }] },
        { field: 'title:', values: [{ text: '', color: 'bg-white' }] },
        { field: 'sample type:', values: [{ text: '', color: 'bg-white' }] },
        { field: 'source name:', values: [{ text: '', color: 'bg-white' }] },
        { field: 'organism:', values: [{ text: '', color: 'bg-white' }] },
        { field: 'characteristics:', values: [{ text: '', color: 'bg-white' }] },
        { field: 'description:', values: [{ text: '', color: 'bg-white' }] }
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
        'Organism',
        'Life stage',
        'Age',
        'Age units',
        'Sex',
        'Ethnicity',
        'Health status',
        'Cell Line',
        'Cell Type',
        'Tissue Type'
        // 'Classification'
      ],
      descriptions: [
        'Specific genomic aspect described by the experiment',
        'Investigative procedure conducted to produce the items',
        'Category of the investigative procedure ',
        'Gene or protein targeted by the experiment',
        'Specific organism from which the biological sample was derived (or cell line established)',
        'Life stage of the organism from which the biological sample was derived (or cell line established,',
        'Age of the organism from which the biological sample was derived (or cell line established,',
        'Unit measure of the age of the organism from which the biological sample was derived (or cell line established,',
        'Sex of the organism from which the biological sample was derived (or cell line established,',
        'Ethnicity of the organism from which the biological sample was derived (or cell line established,',
        'Illness investigated within the sample. This value can be infered by the cell line,',
        'Single cells (natural state), immortalized cell lines, or cells differentiated from specific cell types',
        'A cell type is a classification used to distinguish between morphologically or phenotypically distinct cell forms within a species',
        'Multicellular component in its natural state, or provenance tissue of cell,'
        // 'Kind of material sample used for the experiment'
      ],
      output_fields_common_values: [
        {
          values: ['trascription factor', 'histone'],
          links: [
            'https://en.wikipedia.org/wiki/Transcription_factor#:~:text=In%20molecular%20biology%2C%20a%20transcription,to%20a%20specific%20DNA%20sequence.',
            'https://en.wikipedia.org/wiki/Histone'
          ]
        },
        {
          values: ['chip-seq', 'rna-seq', 'dnase-seq'],
          links: [
            'https://en.wikipedia.org/wiki/ChIP_sequencing',
            'https://en.wikipedia.org/wiki/RNA-Seq',
            'https://en.wikipedia.org/wiki/DNase-Seq'

          ]
        },
        {
          values: ['dna binding', 'transcription', 'dna accessibility', 'rna binding'],
          links: [
            'https://en.wikipedia.org/wiki/DNA-binding_protein',
            'https://en.wikipedia.org/wiki/Transcription_(biology)',
            undefined,
            'https://en.wikipedia.org/wiki/RNA-binding_protein'
          ]
        },
        {
          values: ['h3k4me3', 'h3k27ac', 'ep300', 'ctcf'],
          links: [
            'https://en.wikipedia.org/wiki/H3K4me3',
            'https://en.wikipedia.org/wiki/H3K27ac',
            'https://en.wikipedia.org/wiki/EP300',
            'https://en.wikipedia.org/wiki/CTCF'
          ]
        },
        // {
        //   values: ['whole organism', 'k562', 'forelimb', 'A549'],
        //   links: [
        //     'https://en.wikipedia.org/wiki/Organism',
        //     'https://en.wikipedia.org/wiki/K562_cells',
        //     'https://en.wikipedia.org/wiki/Forelimb',
        //     'https://en.wikipedia.org/wiki/A549_cell'
        //   ]
        // },
        {
          values: ['homo sapiens', 'mus musculus'],
          links: [
            'https://en.wikipedia.org/wiki/Human',
            'https://en.wikipedia.org/wiki/House_mouse'
          ]
        },
        {
          values: ['embryonic', 'child', 'adult'],
          links: [
            undefined,
            undefined,
            undefined
          ]
        },
        {
          values: ['integer positive number'],
          links: [
            undefined
          ]
        },
        {
          values: ['month', 'year', 'week'],
          links: [
            undefined,
            undefined,
            undefined
          ]
        },
        {
          values: ['female', 'male', 'hermaphrodite'],
          links: [
            undefined,
            undefined,
            undefined
          ]
        },
        {
          values: ['white', 'caucasian', 'hispanic'],
          links: [
            undefined,
            undefined,
            undefined
          ]
        },
        {
          values: ['healthy', 'breast cancer', 'cervical adenocarcinoma'],
          links: [
            undefined,
            undefined,
            'https://en.wikipedia.org/wiki/Cervical_cancer'
          ]
        },
        {
          values: ['mcf-7', 'k562', 'lncap', 'hela'],
          links: [
            'https://en.wikipedia.org/wiki/MCF-7',
            'https://en.wikipedia.org/wiki/K562_cells',
            'https://en.wikipedia.org/wiki/LNCaP',
            'https://en.wikipedia.org/wiki/HeLa'
          ]
        },
        {
          values: ['epithelium', 'embryonic stem cell', 't lymphocyte'],
          links: [
            'https://en.wikipedia.org/wiki/Epithelium',
            'https://en.wikipedia.org/wiki/Embryonic_stem_cell',
            'https://en.wikipedia.org/wiki/T_cell'
          ]
        },
        {
          values: ['lung', 'prostate', 'breast'],
          links: [
            undefined,
            undefined,
            undefined
          ]
        }
        // {
        //   values: ['cell line', 'tissue', 'primary cell', 'whole organism'],
        //   links: [
        //     undefined,
        //     undefined,
        //     undefined,
        //     undefined
        //   ]
        // }
      ],
      output_fields_names: [
        'Feature',
        'Technique',
        'Technique Type',
        'Target',
        'Species',
        'Life Stage',
        'Age',
        'Age units',
        'Sex',
        'Ethnicity',
        'Disease',
        'Cell Line',
        'Cell Type',
        'Tissue'
        // 'Biosample Type'
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
          'Organism',
          'Life stage',
          'Age',
          'Age units',
          'Sex',
          'Ethnicity',
          'Health status',
          'Cell Line',
          'Cell Type',
          'Tissue Type'
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
          this.inputIndexes = [
            { end: 0, begin: 0 },
            { end: 0, begin: 0 },
            { end: 0, begin: 0 },
            { end: 0, begin: 0 },
            { end: 0, begin: 0 },
            { end: 0, begin: 0 },
            { end: 0, begin: 0 }
          ]
          for (const [index, value] of this.gradientResults[0][0].entries()) {
            if (value.text === '[gse]:') {
              this.inputIndexes[0].begin = index + 1
            }
            if (value.text === ' [title]:') {
              this.inputIndexes[0].end = index
              this.inputIndexes[1].begin = index + 1
            }
            if (value.text === ' [sample') {
              this.inputIndexes[1].end = index
            }
            if (value.text === ' type]:') {
              this.inputIndexes[2].begin = index + 1
            }
            if (value.text === ' [source') {
              this.inputIndexes[2].end = index
            }
            if (value.text === ' name]:') {
              this.inputIndexes[3].begin = index + 1
            }
            if (value.text === ' [organism]:') {
              this.inputIndexes[3].end = index
              this.inputIndexes[4].begin = index + 1
            }
            if (value.text === ' [characteristics]:') {
              this.inputIndexes[4].end = index
              this.inputIndexes[5].begin = index + 1
            }
            if (value.text === ' [description]:') {
              this.inputIndexes[5].end = index
              this.inputIndexes[6].begin = index + 1
            }
          }
          this.inputIndexes[6].end = this.gradientResults[0][0].length
          this.gpt2Computed = true
          this.loadGpt2 = false
          this.disableGpt2button = true
          let selectedIndex = 0
          for (const newIndex in this.correctionTable) {
            if (this.correctionTable[newIndex].confidence <= this.greenThreshold) {
              selectedIndex = newIndex
              break
            }
          }
          this.visualize(selectedIndex)
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
        // this.inputs[0].values[0].text = this.table_json[this.tableType][this.id].input
      }
      if (this.datasetType === 2) {
        this.inputs_api[0].values[0].text = this.table_json[this.tableType][this.id].input
        // this.inputs[0].values[0].text = this.table_json[this.tableType][this.id].input
      }
      this.isValid = true
      this.disableGpt2button = false
      this.last_index = 'no_index'
      this.callModel()
    },
    visualize (index) {
      if (this.last_index !== index) {
        this.$nextTick(() => {
          this.$refs.outputField[index].click()
        })
      }
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
          for (const i of Array(this.inputs.length).keys()) {
            this.inputs[i].values = this.gradientResults[index][0].slice(this.inputIndexes[i].begin, this.inputIndexes[i].end)
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
      for (const x of Array(this.inputs.length).keys()) {
        this.inputs[x].values = [{ text: '', color: 'bg-white' }]
      }
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
      const maxStatus = this.getSampleWithMaxWarns()
      if (maxStatus.id !== null) {
        this.selected = [{ id: maxStatus.id }]
        this.searchData()
      }
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
        if (row.fields[field].confidence < this.redThreshold) {
          nWarn += 1
        }
      }
      return nWarn
    },
    checkAtLeastOneCorrection () {
      for (const output of this.correctionTable) {
        if (output.fixed === true) return true
      }
      return false
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
        { table: this.table_json, table_id: this.datasetType }
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
        JSON.stringify(this.table_json),
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
    getLoadStatus () {
      this.$axios.get(this.backendIP + '/getGenerateStatus')
        .then(responde => {
          this.loadStatus = Math.round(responde.data)
          console.log(this.loadStatus)
          if (this.loadStatus < 100) this.getLoadStatus()
        }).catch(error => console.log(error))
    },
    loadSamples () {
      this.loadingSamples = true
      this.$axios.post(
        this.backendIP + '/generateTable',
        { output_fields: this.output_fields[2], exp_id: 2, data: this.GSMS_data }
      ).then(response => {
        this.$axios.get(this.backendIP + '/getJSONs')
          .then((response) => {
            this.table_json.corrected = response.data[0]
            this.table_json.principal = response.data[1]
            this.loadingSamples = false
            this.uploadSamples = false
            this.show_error = false
            this.resetPage()
          }).catch(error => (error.message))
      }).catch(error => {
        this.loadingSamples = false
        this.disableLoadSamples = true
        this.show_error = true
        console.log(error)
        this.error_text = 'Something went wrong with the loading'
      })
      this.loadStatus = 0
      this.getLoadStatus()
    },
    loadText () {
      var reader = new FileReader()
      reader.onload = (e) => {
        // console.log(reader.result)
        this.GEO_list_text = reader.result
        this.fileGEO = null
      }
      reader.readAsText(this.fileGEO)
    },
    searchSamples () {
      if (this.GEO_list_text.trim() === '') {
        this.GSMS_data = []
        return
      }
      this.show_error = false
      this.searchingSamples = true
      const searchList = this.GEO_list_text.trim().replace('"', '').replace("'", '').split(',').map(elem => elem.trim().toUpperCase())
      // console.log(searchList)
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
        { table_id: 2 }
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
          this.visualize(newIndex)
          break
        }
      }
    },
    getJSON () {
      this.$axios.get(this.backendIP + '/getJSONs')
        .then((response) => {
          this.table_json.corrected = response.data[0]
          this.table_json.principal = response.data[1]
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
      const outputs = []
      for (const output of this.correctionTable) {
        if (output.fixed === true) outputs.push({ field: output.field, value: output.value })
      }
      // console.log(outputs)
      this.$axios.post(
        this.backendIP + '/saveAndTrain',
        {
          input_text: this.table_json[this.tableType][this.id].input,
          outputs: outputs,
          gsm: this.table_json[this.tableType][this.selected[0].id].GSM
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
          this.resetPage()
          const maxStatus = this.getSampleWithMaxWarns()
          if (maxStatus.max === 0) {
            this.zeroWarns = true
          } else {
            this.confirmSaveAndTrain = false
          }
        }).catch(error => {
          console.log(error.message)
          this.confirmSaveAndTrain = false
        })
        this.loadStatus = 0
        this.getLoadStatus()
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
    },
    getSampleWithMaxWarns () {
      let max = -1
      let maxId = null
      for (const [index, row] of this.table_json.principal.entries()) {
        if (this.count_warns(row) > max) {
          max = this.count_warns(row)
          maxId = index
        }
      }
      return { id: maxId, max: max }
    },
    moveAll () {
      let newIndex = this.table_json.corrected.length
      for (const row of this.table_json.principal) {
        row.id = newIndex
        this.table_json.corrected.push(row)
        newIndex += 1
      }
      this.table_json.principal = []
      this.store_json()
      this.resetPage()
    },
    filterFn (val, update) {
      // console.log(this.output_fields[2][[0]])
      update(() => {
        if (val === '') {
          this.filterOptions = this.stringOptions[this.output_fields[2][this.last_index]].filter(
            v => v.length < 40
          )
        } else {
          const needle = val.toLowerCase()
          this.filterOptions = this.stringOptions[this.output_fields[2][this.last_index]].filter(
            v => v.toLowerCase().indexOf(needle) > -1 && v.length < 40
          )
        }
      })
    },
    createValue (val, done) {
      if (val.length > 0) {
        if (!this.stringOptions.includes(val)) {
          this.stringOptions.push(val)
        }
        done(val, 'toogle')
      }
    },
    onInputValue (val) {
      this.edit_text = val
    },
    onPopupShow (val) {
      this.popupOpen = true
    },
    onPopupHide (val) {
      this.popupOpen = false
    },
    onClick (event) {
      if (
        this.popupOpen === true
        // && event.target.nodeName.toLowerCase() === 'input' // only on click in input
      ) {
        event.stopImmediatePropagation()
      }
      // forces popup to show again. Can't avoid flickering
      // this.$refs.input.showPopup()
    },
    exportCSV () {

    }
  },
  created () {
    this.stringOptions.Age = []
    this.columns = this.columns2
    this.$axios.get(this.backendIP + '/getJSONs')
      .then((response) => {
        this.table_json.corrected = response.data[0]
        this.table_json.principal = response.data[1]
        this.resetPage()
      }).catch(error => (error.message))
  }
}
</script>
