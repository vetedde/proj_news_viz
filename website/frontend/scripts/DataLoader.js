let dataloader = null

if (process.env.NODE_ENV === 'development') {
  class DataLoaderDevelopment {}

  dataloader = new DataLoaderDevelopment()
} else if (process.env.NODE_ENV === 'production') {
  class DataLoaderProduction {
    // TODO: write this
  }

  dataloader = new DataLoaderProduction()
}

export default dataloader
