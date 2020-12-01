<template>
  <div class='q-pa-md'>
    <div class='q-pa-md justify-evenly row'>
      <div>
        <div class='row q-pb-md'>
          <q-input
          class='input-id q-pb-md'
          outlined v-model="id"
          label="GEO ID"
          :error='!isValid'
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
        <div class="q-pa-md">
          <q-btn-toggle
            v-model="typeInterpreter"
            class="toggle "
            no-caps
            rounded
            unelevated
            spread
            toggle-color="primary"
            color="white"
            text-color="primary"
            :options="[
              {label: 'Lime', value: 'lime'},
              {label: 'Attention', value: 'attention'}
            ]"
          />
        </div>
        <div class="q-pa-md">
          <q-card class="my-outputs">
            <q-card-section>
              <div class="text-h6 text-primary q-pl-md"> Output</div>
              <div class='q-pa-sm' v-for="(output, index) in outputs" :key="output" @click="visualizeLime(index)">
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
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="sass" scoped>
.my-outputs
  width: 100%
  max-width: 200px
.toggle
  border: 1px solid #027be3
.input-id
  width: 40%
.my-inputs
  width: 380px
</style>

<script>
import json from '../assets/dataset.json'
export default {
  data () {
    return {
      typeInterpreter: 'lime',
      disableGpt2button: true,
      loadGpt2: false,
      loadIcon: false,
      my_value: 'Submit',
      limeComputed: [false, false, false, false],
      gpt2Computed: false,
      isValid: true,
      dataset: json,
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
      outputs: [
        { field: 'Cell Line', value: '', color: 'grey-3' },
        { field: 'Cell Type', value: '', color: 'grey-3' },
        { field: 'Tissue Type', value: '', color: 'grey-3' },
        { field: 'Factor', value: '', color: 'grey-3' }
      ]
    }
  },
  name: 'PageIndex',
  methods: {
    callModel () {
      if (!this.gpt2Computed) {
        this.loadGpt2 = true
        // http://10.79.23.5:5003 or http://localhost:5000/prova2
        this.$axios.post('http://localhost:5000/prova2', this.inputs_api).then((response) => {
          this.outputs = response.data
          this.gpt2Computed = true
          this.loadGpt2 = false
        }).catch(error => (error.message))
      }
    },
    searchData () {
      this.limeComputed = [false, false, false, false]
      this.gpt2Computed = false
      if ((this.id in this.dataset) === false) {
        this.isValid = false
        this.disableGpt2button = true
        return
      }
      for (const x of Array(4).keys()) {
        this.limeResults[x][0] = [{ text: '', color: 'bg-grey-3' }]
        this.limeResults[x][1] = [{ text: '', color: 'bg-grey-3' }]
        this.limeResults[x][2] = [{ text: '', color: 'bg-grey-3' }]
      }
      this.inputs[0].values = [{ text: '', color: 'bg-white' }]
      this.inputs[1].values = [{ text: '', color: 'bg-white' }]
      this.inputs[2].values = [{ text: '', color: 'bg-white' }]
      this.inputs_api[0].values[0].text = this.dataset[this.id].title
      this.inputs_api[1].values[0].text = this.dataset[this.id].description
      this.inputs_api[2].values[0].text = this.dataset[this.id].characteristics
      this.inputs[0].values[0].text = this.dataset[this.id].title
      this.inputs[1].values[0].text = this.dataset[this.id].description
      this.inputs[2].values[0].text = this.dataset[this.id].characteristics
      this.isValid = true
      this.disableGpt2button = false
    },
    visualizeLime (index) {
      if (this.gpt2Computed) {
        if (this.limeComputed[index]) {
          this.inputs[0].values = this.limeResults[index][0]
          this.inputs[1].values = this.limeResults[index][1]
          this.inputs[2].values = this.limeResults[index][2]
        } else {
          this.loadIcon = true
          this.limeComputed[index] = true
          this.$axios.post('http://localhost:5000/prova', { inputs: this.inputs_api, outputs: this.outputs, field: this.outputs[index].field }).then((response) => {
            this.limeResults[index][0] = response.data[0]
            this.limeResults[index][1] = response.data[1]
            this.limeResults[index][2] = response.data[2]
            this.inputs[0].values = response.data[0]
            this.inputs[1].values = response.data[1]
            this.inputs[2].values = response.data[2]
            this.loadIcon = false
          }).catch(error => (error.message))
        }
      }
    }
  }
}
</script>
