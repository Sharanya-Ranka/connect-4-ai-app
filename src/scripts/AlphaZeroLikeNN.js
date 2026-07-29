// Assumes: import * as tf from '@tensorflow/tfjs'
// or <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs"></script>

function createConvolutional4PAndVNetwork(config, channelsFirst = false) {
  const {
    NUM_ROWS: numRows,
    NUM_COLS: numCols,
    NUM_INITIAL_CHANNELS: initialChannels,
    NUM_CNN_FILTERS: numFilters,
    KERNEL_SIZE: kernelSize,
    DROPOUT_RATE: dropoutRate,
    POLICY_HEAD_FILTERS: policyHeadFilters,
    VALUE_HEAD_FILTERS: valueHeadFilters,
  } = config;

  const initialKernelSize = 4;

  // Compute spatial dims after initial conv (no padding)
  const outRows = numRows - initialKernelSize + 1;
  const outCols = numCols - initialKernelSize + 1;
  const flattenedSpatial = outRows * outCols;

  // dataFormat and axis for channel operations
  const dataFormat = channelsFirst ? 'channelsFirst' : 'channelsLast';
  const channelAxis = channelsFirst ? 1 : -1; // used for concat etc.

  // Input shape: TFJS expects [h, w, c] for channelsLast, or [c, h, w] for channelsFirst
  const inputShape = channelsFirst
    ? [initialChannels, numRows, numCols]
    : [numRows, numCols, initialChannels];

  const inp = tf.input({ shape: inputShape });

  // --- Initial conv block ---
  // 1) initial_conv: kernel=4, padding='valid' (no padding)
  let x = tf.layers
    .conv2d({
      filters: numFilters,
      kernelSize: initialKernelSize,
      padding: 'valid',
      dataFormat,
      useBias: false,
    })
    .apply(inp);
  x = tf.layers.batchNormalization({ axis: channelAxis }).apply(x);
  x = tf.layers.activation({ activation: 'relu' }).apply(x);

  // 2) second conv: same padding, kernelSize = kernelSize, filters = numFilters
  let x1 = tf.layers
    .conv2d({
      filters: numFilters,
      kernelSize,
      padding: 'same',
      dataFormat,
      useBias: false,
    })
    .apply(x);
  x1 = tf.layers.batchNormalization({ axis: channelAxis }).apply(x1);
  x1 = tf.layers.activation({ activation: 'relu' }).apply(x1);

  // Concatenate along channel axis: this produces 2 * numFilters channels
  const xCat = tf.layers.concatenate({ axis: channelAxis }).apply([x, x1]);

  // --- Policy head ---
  // 1x1 conv to reduce channels
  let policyX = tf.layers
    .conv2d({
      filters: policyHeadFilters,
      kernelSize: 1,
      padding: 'valid',
      dataFormat,
      useBias: false,
    })
    .apply(xCat);
  policyX = tf.layers.batchNormalization({ axis: channelAxis }).apply(policyX);
  policyX = tf.layers.activation({ activation: 'relu' }).apply(policyX);

  // Flatten then dropout + dense layers
  policyX = tf.layers.flatten().apply(policyX); // shape: [batch, flattenedSpatial * policyHeadFilters]
  policyX = tf.layers.dropout({ rate: dropoutRate }).apply(policyX);

// compute intermediate dense sizes same as PyTorch version:
  const policyHeadFlattenedSize = flattenedSpatial * policyHeadFilters;
  const policyDense1Size = Math.floor(policyHeadFlattenedSize / 2) || 1;

  policyX = tf.layers.dense({ units: policyDense1Size, activation: 'relu' }).apply(policyX);
  const policyLogits = tf.layers.dense({ units: numCols, activation: null }).apply(policyX);
  // policyLogits shape: [batch, numCols]  (logits for each column)

  // --- Value head ---
  let valueX = tf.layers
    .conv2d({
      filters: valueHeadFilters,
      kernelSize: 1,
      padding: 'valid',
      dataFormat,
      useBias: false,
    })
    .apply(xCat);
  valueX = tf.layers.batchNormalization({ axis: channelAxis }).apply(valueX);
  valueX = tf.layers.activation({ activation: 'relu' }).apply(valueX);

  valueX = tf.layers.flatten().apply(valueX);
  valueX = tf.layers.dropout({ rate: dropoutRate }).apply(valueX);

  const valueHeadFlattenedSize = flattenedSpatial * valueHeadFilters;
  const valueDense1Size = Math.floor(valueHeadFlattenedSize / 2) || 1;

  valueX = tf.layers.dense({ units: valueDense1Size, activation: 'relu' }).apply(valueX);
  let valueLin = tf.layers.dense({ units: 1, activation: null }).apply(valueX);
  // compress to [-1, +1] using tanh and flatten final dim
  let valueOut = tf.layers.activation({ activation: 'tanh' }).apply(valueLin);
  // valueOut shape: [batch, 1]. Optionally squeeze last dim in training/eval code.

  const model = tf.model({ inputs: inp, outputs: [valueOut, policyLogits] });

  return model;
}

/* ---------------------------
Example usage:

const config = {
  NUM_ROWS: 6,
  NUM_COLS: 7,
  NUM_INITIAL_CHANNELS: 3,
  NUM_CNN_FILTERS: 64,
  KERNEL_SIZE: 3,
  DROPOUT_RATE: 0.3,
  POLICY_HEAD_FILTERS: 32,
  VALUE_HEAD_FILTERS: 32
};

const model = createConvolutional4PAndVNetwork(config, channelsFirst= false);
model.summary();

// Compile if you want:
// model.compile({
//   optimizer: tf.train.adam(1e-3),
//   loss: {
//     0: tf.losses.meanSquaredError, // value head
//     1: tf.losses.softmaxCrossEntropy // policy head (note: in tfjs you usually pass arrays, see below)
//   }
// });

// When training or predicting, recall the model returns [valueBatch, policyLogitsBatch].
// If you want the value as shape [batch] instead of [batch, 1], call `.reshape([batch])` or squeeze the last dim.
// --------------------------- */

