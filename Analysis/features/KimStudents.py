from .features import *
from ..constants import *
from .. import variant_functions as vf


class PhenotypeFeature(NominalFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, name="phenotypes", *args, **kwargs)

	def add_row(self, row):
		hpo_list = re.split('[;,]', row['Phenotype'])
		for term in hpo_list:
			try:
				if term.casefold() is 'none':
					super().update(row, term)
				if term.casefold() not in NULL_TERMS:
					var_hpo = vf.generalized_vhl_phenotype(term.strip())
					super().update(row, var_hpo)
			except ValueError as e:
				self.logger.warning(repr(e))


class VariantTypeFeature(NominalFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, name="variant_type", *args, **kwargs)

	def add_row(self, row):
		so_list = re.split('[;,]', row['Mutation Type'])
		for term in so_list:
			try:
				if term.casefold() not in NULL_TERMS:
					var_obo = vf.get_valid_obo(term.strip())
					super().update(row, var_obo)
			except ValueError as e:
				self.logger.warning(repr(e))


class DeNovoFeature(NominalFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, name="de_novo", *args, **kwargs)

	def add_row(self, row):
		super().update_by_column(row, "Confirmed De Novo")


class SexFeature(NominalFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, name="sex", *args, **kwargs)

	def add_row(self, row):
		super().update_by_column(row, "Sex")


class DomainFeature(NominalFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, name="domain", *args, **kwargs)

	def add_row(self, row):
		cdna = vf.get_valid_cdna(row["Mutation Event c.DNA."])
		for domain in vf.affected_domains(cdna):
			super().update(row, domain)


class MultipleMutationFeature(NominalFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, name="multiple", *args, **kwargs)

	def add_row(self, row):
		super().update_by_column(row, "Multiple Mutants in Case")


class EvaluatedAgeFeature(RatioFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, name="evaluated_age", *args, **kwargs)

	def add_row(self, row):
		match = EVALUATED_AGE_REGEX.search(row['Age'])
		if match is not None:
			var = match.groupdict()
			months = 0
			if var['Y'] is not None:
				months += int(var['Y']) * 12
			if var['M'] is not None:
				months += int(var['M'])

			if not(var['Y'] is None and var['M'] is None):
				super().update(row, months)


class LastKnownAgeFeature(RatioFeature):
	def __init__(self, *args, **kwargs):
		super().__init__(self, name="last_known_age", *args, **kwargs)

	def add_row(self, row):

		lk_match = LASTKNOWN_AGE_REGEX.search(row['Age'])
		e_match = EVALUATED_AGE_REGEX.search(row['Age'])
		if lk_match is not None:
			var = lk_match.groupdict()
			months = 0
			if var['Y'] is not None:
				months += int(var['Y']) * 12
			if var['M'] is not None:
				months += int(var['M'])

			if not(var['Y'] is None and var['M'] is None):
				super().update(row, months)

		elif e_match is not None:
			var = e_match.groupdict()
			months = 0
			if var['Y'] is not None:
				months += int(var['Y']) * 12
			if var['M'] is not None:
				months += int(var['M'])
			if not(var['Y'] is None and var['M'] is None):
				super().update(row, months)

		else:
			pass
