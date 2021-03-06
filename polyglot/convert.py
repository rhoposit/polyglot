"""
Convert langid.py model to one suitable for use in multilangid.py.
The main issue is that we need to renormalize P(t|C) as it is stored as
log-prob in langid.py.

Marco Lui, March 2013
"""
import argparse, os
import numpy as np
import bz2, base64
import logging

from cPickle import loads, dumps

from identifier import MultiLanguageIdentifier

logger = logging.getLogger(__name__)

def read_nb_model(path):
  logger.info("reading model from {0}".format(path))

  if os.path.isdir(path):
    path = os.path.join(path, 'model')

  with open(path) as f:
    model = loads(bz2.decompress(base64.b64decode(f.read())))
  nb_ptc, nb_pc, nb_classes, tk_nextmove, tk_output = model
  nb_numfeats = len(nb_ptc) / len(nb_pc)
  nb_ptc = np.array(nb_ptc).reshape(len(nb_ptc)/len(nb_pc), len(nb_pc))
  logger.debug("ptc shape: {0}".format(nb_ptc.shape))

  # Normalize to 1 on the term axis
  for i in range(nb_ptc.shape[1]):
    logger.debug("normalizing row {0} of {1}".format(i+1, nb_ptc.shape[1]))
    nb_ptc[:,i] = (1/np.exp(nb_ptc[:,i][None,:] - nb_ptc[:,i][:,None]).sum(1))

  return (nb_classes, nb_ptc, tk_nextmove, tk_output)

def write_polyglot_model(model, path):
  logger.info("writing converted model to {0}".format(path))
  # TODO: Validate model
  # nb_classes, nb_ptc, tk_nextmove, tk_output = model
  output = base64.b64encode(bz2.compress(dumps(model)))
  with open(path, 'w') as f:
    f.write(output)
  logger.info("wrote {0} bytes".format(len(output)))

def read_polyglot_model(path):
  with open(path) as f:
    return MultiLanguageIdentifier.unpack_model(f.read())


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--verbose','-v',action="store_true")
  parser.add_argument('model', metavar="MODEL_DIR", help="path to langid.py training model dir")
  parser.add_argument('output', metavar="OUTPUT", help="produce output in")
  args = parser.parse_args()

  logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING)
  
  model = read_nb_model(args.model)
  write_polyglot_model(model, args.output)

if __name__ == "__main__":
  main()
