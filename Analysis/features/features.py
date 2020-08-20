import re
import logging
import numpy as np

EVALUATED_AGE_REGEX = re.compile("E((?P<Y>[0-9]+)Y)?((?P<M>[0-9]+)M)?")
LASTKNOWN_AGE_REGEX = re.compile("lk((?P<Y>[0-9]+)Y)?((?P<M>[0-9]+)M)?")

class Feature:
	def __init__(self, *args, name="Feature", column=None, **kwargs):
		self.name = name
		self.column = column
		self.logger = logging.getLogger(self.name)

	def filter(self, row):
		if row is not None:
			return True

	def update_by_column(self, row, column):
		category = row[column].casefold()
		self.update(row, category)

	def add_category(self, category):
		self.rows[category] = self.rows.get(category, [])

	def update(self, row, category):
		self.add_category(category)
		self.rows[category].append(row)

class NominalFeature(Feature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.rows = {}

	def sort(self):
		keys = np.array(list(self.rows.keys()))
		counts = [len(v) for v in self.rows.values()]
		c_order = np.argsort(counts)
		k_order = keys[c_order]
		old_rows = self.rows
		self.rows = {k: old_rows[k] for k in k_order}

	def to_dict(self):
		return {f'{self.name}_{k}': self.rows[k] for k in self.rows.keys()}



class OrdinalFeature(NominalFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)


class IntervalFeature(Feature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.rows = []
		self.values = []
		self.histogram = NominalFeature(name=f'{self.name}_hist')

	def add_category(self, category):
		pass

	def update(self, row, value):
		self.values.append(value)
		self.rows.append(row)

	def make_hist(self, n_bins=10):
		values = np.array(self.values)
		bins = np.histogram_bin_edges(values, bins=n_bins)
		values_bins = np.digitize(values, bins)

		for i in range(len(bins)-1):
			category = f'{int(bins[i])}-{int(bins[i+1])}'
			self.histogram.add_category(category)

		for i in range(len(self.rows)):
			v_bin = values_bins[i]
			if v_bin == len(bins):
				v_bin -= 1
			bin_lower = int(bins[v_bin-1])
			bin_upper = int(bins[v_bin])

			self.histogram.update(self.rows[i], f'{bin_lower}-{bin_upper}')

	def to_dict(self):
		self.make_hist()

		out_dict = self.histogram.to_dict()
		# out_dict = {}
		# out_dict[f"{self.name}_min"] = sorted_values[0]
		# out_dict[f"{self.name}_max"] = sorted_values[-1]
		#
		# for i in range(len(bins)-1):
		# 	out_dict[f"{self.name}_{int(bins[i])}-{int(bins[i+1])}"] = hist[i]

		return out_dict


class RatioFeature(IntervalFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)

