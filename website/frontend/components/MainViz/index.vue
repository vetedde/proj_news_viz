<template>
  <div class="container-fluid w-100">
    <div class="row">
      <div class="col-12 col-sm-8 col-md-9">
        Plot
      </div>
      <div class="col-12 col-sm-4 col-md-3">
        <b-form-group id="input-group-1" label="Источник:" label-for="input-1">
          <b-form-select
            id="input-1"
            v-model="sourceSelected"
            :options="sourceOptions"
            size="sm"
          ></b-form-select>
        </b-form-group>

        <b-form-group id="input-group-2" label="Тип графика:">
          <b-form-radio-group
            id="btn-radios-1"
            v-model="plotTypeSelected"
            :options="plotTypeOptions"
            buttons
            button-variant="outline-secondary"
            size="sm"
            name="radio-btn-outline"
          ></b-form-radio-group>
        </b-form-group>

        <b-form-group id="input-group-3" label="Рубрики:" label-for="input-3">
          <b-form-select
            id="input-3"
            v-model="rubricSelected"
            :options="rubricOptions"
            size="sm"
          ></b-form-select>
        </b-form-group>

        <b-form-group id="input-group-4" label="Темы:" label-for="input-4">
          <multiselect
            id="input-4"
            v-model="topicSelected"
            :options="topicOptions"
            :searchable="false"
            :close-on-select="false"
            :show-labels="false"
            :multiple="true"
            placeholder="Темы"
          ></multiselect>
        </b-form-group>

        <b-form-group id="input-group-5" label="Дополнительные данные:" label-for="input-5">
          <multiselect
            id="input-5"
            v-model="extraDataSelected"
            :options="extraDataOptions"
            :searchable="false"
            :close-on-select="false"
            :show-labels="false"
            :multiple="true"
            placeholder="Дополнительные данные"
          ></multiselect>
        </b-form-group>
      </div>
    </div>
  </div>
</template>

<script>
import Multiselect from 'vue-multiselect'

export default {
  components: {
    Multiselect
  },
  data() {
    return {
      sourceOptions: ['Лента'],
      sourceSelected: null,

      plotTypeOptions: ['Ridge Plot', 'Bump Chart'],
      plotTypeSelected: null,

      rubricOptions: ['Мир', 'Культура'],
      rubricSelected: null,

      topicOptions: ['Лента'],
      topicSelected: null,

      extraDataOptions: ['Лента'],
      extraDataSelected: null
    }
  }
}
</script>

<style lang="scss" scoped></style>
