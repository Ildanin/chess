from chessAI import ChessAI, load_chessAI
from chessAI.data import get_data
from config import INFO, ACTIVATOR, NORMALIZER, FACTOR_RANGE, BIAS_RANGE, ALPHA, MOMENTUM_RATE, CYCLES

#ai = ChessAI(INFO, ACTIVATOR, NORMALIZER, FACTOR_RANGE, BIAS_RANGE)
ai = load_chessAI("ChessAI2.txt")

train_x, train_y = get_data("data.txt", 2500, 5000)

#ai.train_stochastic_momentum(train_x, train_y, ALPHA, MOMENTUM_RATE, CYCLES, 2000, True)
ai.train_vanilla(train_x, train_y, 0.01, 10, True)
ai.save("ChessAI3.txt")