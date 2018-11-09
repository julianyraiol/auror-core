import os
import yaml

class Params(object):

    def __init__(self, name="params", **key_vals):
        self.name = name
        self.key_vals = key_vals
        self.properties = dict(config=dict())

    def _get_items(self):
        return self.key_vals.items()

    def _add_items(self):
        self.properties['config'] = dict(self._get_items())

    def _write(self, folder):
        name = os.path.basename(folder)
        path = "{}.flow".format(os.path.join(folder, name))
        with open(path, 'rb') as reader:
            data = yaml.load(reader)
        data.update(self.properties)

        with open(path, 'wb') as writer:
            writer.write(
                yaml.dump(data, default_flow_style=False)
            )

class Env(Params):

    def _get_items(self):
        return [("env.{}".format(name), value) for name, value in self.key_vals.items()]


class SparkConfig(Params):
    
    def _get_items(self, prepend=""):
        return [(name, "--conf {}{}={}".format(prepend, name, value)) for name, value in self.key_vals.items()]


class SparkExecutor(SparkConfig):

    def _get_items(self):

        return super(SparkExecutor, self)._get_items("spark.executorEnv.")


class SparkDriver(SparkConfig):

    def _get_items(self):

        return super(SparkDriver, self)._get_items("spark.yarn.appMasterEnv.")


class ParamsJoin(Params):

    def __init__(self, param_name="custom.envs", separator=" "):
        self.param_name = param_name
        self.separator = separator
        self.properties = dict(config=dict())
        self.params_class = []

    def __call__(self, *params_class):
        self.params_class = params_class
        return self

    def _add_items(self):
        param_props = []
        for param_class in self.params_class:
            for name, value in param_class._get_items():
                param_props.append(value)
        self.properties[self.param_name] = self.separator.join(param_props)