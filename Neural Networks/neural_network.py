import numpy as np
from sklearn.datasets import load_iris
import time
import sys
import warnings

warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

def binary(x):
    return [1 if y>0 else 0 for y in x]

def binary_deriv(x):
    return [sys.maxsize if y==0 else 0 for y in x]

def sigmoid(x):
    return 1/(1+np.exp(-x))

def sigmoid_deriv(x):
    return x*(1-x)

def tanh(x):
    return np.tanh(x)

def tanh_deriv(x):
    return 1.-np.tanh(x)**2

TRAINING_ERRORS = []
TESTING_ERRORS = []
NUMBER_OF_EPOCHS = 5000
LEARNING_RATE = 0.5
BATCH_SIZE = 5
LAYERS = [4, 7, 7, 3]
ACTIVATION = sigmoid
ACTIVATION_DERIV = locals()[ACTIVATION.__name__ + "_deriv"]

class NerualNetwork:
    def __init__(self, layer_sizes, batch_size=BATCH_SIZE, activation=ACTIVATION, bias_enabled=True):
        self.bias_enabled = bias_enabled
        self.activation = activation
        self.activation_deriv = globals()[activation.__name__ + "_deriv"]
        self.input_size = layer_sizes[0]
        self.output_size = layer_sizes[-1]
        self.batch_size = batch_size
        self.hidden_layers = len(layer_sizes) - 2
        self.weights = []
        for i in range(1, len(layer_sizes) - 1):
            self.weights.append(self.init_layer_weights(layer_sizes[i-1] + int(self.bias_enabled), layer_sizes[i] + int(self.bias_enabled)))
        self.weights.append(self.init_layer_weights(layer_sizes[i] + int(self.bias_enabled), layer_sizes[i+1]))

    def init_layer_weights(self, source_layer_size, destination_layer_size):
        return 2 * np.random.random((source_layer_size, destination_layer_size)) - 1

    def divide_training_data_to_batches(self, training_data):
        np.random.shuffle(training_data)
        return np.array_split(training_data, int(len(training_data) / self.batch_size))

    def convert_output_to_vector(self, output):
        return np.array([1 if output == i else 0 for i in range(self.output_size)])

    def train(self, inputs, outputs, training_amount, epochs=NUMBER_OF_EPOCHS, learning_rate=LEARNING_RATE):
        if self.bias_enabled:
            biases = np.atleast_2d(np.ones(inputs.shape[0]))
            inputs = np.concatenate((biases.T, inputs), axis=1)
        
        full_data = list(zip(inputs, outputs))
        np.random.shuffle(full_data)
        training_data, testing_data = full_data[:training_amount], full_data[training_amount:]

        for epoch in range(epochs):
            training_full_data = training_data
            batches = self.divide_training_data_to_batches(training_full_data)
            epoch_training_error = np.zeros(self.output_size)

            for batch_index in range(len(batches)):
                current_batch = batches[batch_index]
                batch_deltas = [np.zeros(i.shape[1]) for i in self.weights]
                batch_deltas.reverse()

                for current_input, current_output in current_batch:
                    current_layers = [current_input.T]
                    for layer in range(len(self.weights)):
                        current_layers.append(self.activation(np.dot(current_layers[layer], self.weights[layer])))
                    
                    error = self.convert_output_to_vector(current_output) - current_layers[-1]
                    epoch_training_error += np.mean(np.abs(error))

                    deltas = [(error * self.activation_deriv(current_layers[-1])) / self.batch_size]
                    
                    # Calculating deltas, only for intermisiate weights 
                    for layer in range(len(current_layers) - 2, 0, -1):
                        deltas.append((np.dot(deltas[-1], self.weights[layer].T) * self.activation_deriv(current_layers[layer])) / self.batch_size)
                    
                    batch_deltas += deltas
                    
                batch_deltas[:] = batch_deltas[::-1]

                #Back propagation - Gradient Descent Weights Update
                for i in range(len(self.weights)):
                    layer = np.atleast_2d(current_layers[i])
                    delta = np.atleast_2d(batch_deltas[i])
                    self.weights[i] += learning_rate * np.dot(layer.T, delta)
            
            epoch_training_error = np.mean(epoch_training_error)
            epoch_testing_error = np.mean(self.test(testing_data))
            
            if epoch % 1000 == 0:
                print("Epoch #{0} finished. Train Error: {1}\t Test Error: {2}".format(epoch, epoch_training_error, epoch_testing_error))
            
            TESTING_ERRORS.append(epoch_testing_error)
            TRAINING_ERRORS.append(epoch_training_error)
            
    def test(self, testing_data):
        epoch_testing_error = np.zeros(self.output_size) 
        for current_input, current_output in testing_data:
            current_layers = [current_input.T]
            
            for layer in range(len(self.weights)):
                current_layers.append(self.activation(np.dot(current_layers[layer], self.weights[layer])))
            
            epoch_testing_error += np.mean(np.abs(self.convert_output_to_vector(current_output) - current_layers[-1]))
        
        return epoch_testing_error


def main():
    iris = load_iris()
    nerual_network = NerualNetwork(LAYERS)
    start=time.time()
    nerual_network.train(iris.data, iris.target, 100) 
    
    print("Training took: " + str(time.time() - start) + " seconds")
    
    with open("training_errors_{0}_{1}_{2}_{3}.txt".format(NUMBER_OF_EPOCHS, int(10*LEARNING_RATE), BATCH_SIZE, ACTIVATION.__name__), 'w') as f:
        for n in TRAINING_ERRORS: f.write("{}\n".format(n))
    with open("testing_errors_{0}_{1}_{2}_{3}.txt".format(NUMBER_OF_EPOCHS, int(10*LEARNING_RATE), BATCH_SIZE, ACTIVATION.__name__), 'w') as f:
        for n in TESTING_ERRORS: f.write("{}\n".format(n))

if __name__ == '__main__':
    main()