import re
import itertools
import functools
import collections

''' ##############################################################

    ##############################################################
'''
class OPaCRegex:

    def __init__(self):
        self.samples = []

    def digest(self, samples):

        templates = {}
        for sample in samples:
            sample = Sample(sample)

            template = tuple(sample.template)

            if template not in templates:
                templates[template] = []
            templates[template].append(sample)

        # Select Best Template and Its samples
        sorted_templates = [(len(samples), template) for template, samples in templates.items()]
        sorted_templates.sort(reverse=True)
        best_template = sorted_templates[0][1]
        self.samples = templates[best_template]

        template = []
        for group_index in range(0, len(best_template)):
            group = RegexGroup(best_template[group_index], group_index)
            for sample in self.samples:
                group.set_sample(sample)
            template.append(group)

        regex = ''
        for group in template:
            group.sharpen()
            regex += group.compile()

        return regex


''' ##############################################################

    ##############################################################
'''
class RegexGroup:
    def __init__(self, template, index):
        self.index = index
        self.template = [template]
        self.heights = [set()]
        self.cardinalities = []
        self.cardinalities.append([set() for token_regex in self.template[0]])
        self.samples = []


    def set_sample(self, sample):

        tokens_samples = sample.group(self.index)

        self.heights[0].add(sample.heights[self.index])

        for token_index in range(0, len(self.template[0])):
            cardinalities = [len(token_sample) for token_sample in tokens_samples[token_index]]
            self.cardinalities[0][token_index].update(cardinalities)

        self.samples.append(tokens_samples)


    def sharpen(self):
        
        template_fixes = {0:[], -1:[]} # prefix, postfix
        cardinalities_fixes = {0:[], -1:[]}

        self.template[0] = list(self.template[0])
        for token_index in range(0, len(self.template[0])):
            token_samples = [sample[token_index] for sample in self.samples]

            unique_samples = list(set(itertools.chain(*token_samples)))
            if len(unique_samples) == 1:
                self.template[0][token_index] = re.escape(unique_samples[0])
                self.cardinalities[0][token_index] = {1}

            for fix_index in template_fixes:
                fix_tokens = set([token_sample[fix_index] for token_sample in token_samples])
                if len(fix_tokens) == 1:
                    template_fixes[fix_index].append(re.escape(fix_tokens.pop()))
                    cardinalities_fixes[fix_index].append({1})
                else:
                    template_fixes[fix_index].append(self.template[0][token_index])
                    cardinalities_fixes[fix_index].append(self.cardinalities[0][token_index])

        self.template[0] = tuple(self.template[0])

        heights = []
        cardinalities = []
        template = self.template[0]
        for fix_index in template_fixes:
            if not self.heights[0]:
                break
            fix = tuple(template_fixes[fix_index])
            if fix != template:
                insert_index = fix_index * (-len(self.template))
                self.template.insert(insert_index, fix)
                cardinalities.insert(insert_index, cardinalities_fixes[fix_index])

                heights.insert(insert_index, [1])
                self.heights[0] = [(height-1) for height in self.heights[0] if (height-1)]

        heights.insert(1, self.heights[0])
        self.heights = heights

        cardinalities.insert(1, self.cardinalities[0])
        self.cardinalities = cardinalities


    def cardinality_token(self, cardinality):
        cardinality = list(cardinality)

        if len(cardinality) > 2:
            return '+'

        elif len(cardinality) == 2:
            cardinality.sort()
            return '{{{0},{1}}}'.format(*cardinality)

        elif (len(cardinality) == 1) and (cardinality[0] > 1):
            return '{{{0}}}'.format(*cardinality)

        return ''


    def compile(self):

        regex = ''
        for group_index in range(0, len(self.template)):
            if not self.heights[group_index]:
                continue

            subregex = ''
            for token_index in range(0, len(self.template[group_index])):
                subregex += self.template[group_index][token_index]
                subregex += self.cardinality_token(self.cardinalities[group_index][token_index])

            group_cardinality = self.cardinality_token(self.heights[group_index])
            if group_cardinality:
                subregex = '({0}){1}'.format(subregex, group_cardinality)

            regex += subregex

        return regex


''' ##############################################################

    ##############################################################
'''
class Sample:

    def __init__(self, sample):
        template = self.digest_tokens(sample)
        template = self.fragment(template)
        self.template, self.heights = self.compress(template)
        self.weights = [len(group) for group in self.template]
        

    def __hash__(self):
        return hash(tuple(self.template))

    def group(self, group_index):
        samples = []

        weight = self.weights[group_index]
        height = self.heights[group_index]
        last_index = sum([self.weights[index]*self.heights[index] for index in range(0, group_index)])
        for token_index in range(last_index, last_index + height*weight, weight):
            samples.append(self.tokens[token_index:token_index+weight])

            last_token_index = token_index + weight

        return list(zip(*samples))

    def digest_tokens(self, sample):
        self.tokens = re.findall('([^\W_]+|[\W_]+)', sample)

        word_regex = '[^\W_]'
        delimiters = collections.Counter([token for token in self.tokens if len(token) == 1]).most_common(2)
        if delimiters:
            delimiters = list(zip(*delimiters))[0]
            delimiter = delimiters[0]
            #self.tokens = re.findall('([^\W]+|[\W_]+)', sample)
            if delimiter == '-':
                word_regex = '[^\W]'

        template = []
        group = []
        tokens = []
        for token in self.tokens:

            if re.match('^\d+$', token):
                regex_token = '\d'

            elif group and re.match(group[-1], token):
                tokens[-1] += token
                continue

            elif re.match('[^\W_]+', token[0]):
                regex_token = word_regex

            else:
                regex_token = re.escape(token)

            if regex_token in group:
                template.append(tuple(group))
                group = []

            tokens.append(token)
            group.append(regex_token)

        template.append(tuple(group))
        self.tokens = tokens

        return template


    def fragment(self, template):
        fragmented_template = []
        sizes = []

        last_group = template.pop(0)
        while template:
            group = template.pop(0)

            intersection_size = 0
            for size in range(1, min(len(last_group), len(group)) + 1):
                if last_group[-1*size:] == group[:size]:
                    intersection_size = size
                    break

            if intersection_size:
                fragments = [last_group[:-1*intersection_size],
                             last_group[ -1*intersection_size:],
                             group[:intersection_size],
                             group[intersection_size:]]
                fragments = [group for group in fragments if group]

                last_group = fragments.pop()
                fragmented_template.extend(fragments)

            else:
                fragmented_template.append(last_group)
                last_group = group

        fragmented_template.append(last_group)
        return fragmented_template


    def compress(self, template):
        result = []
        sizes = []

        group_size = 1
        last_group = template.pop(0)
        while template:
            group = template.pop(0)
            if last_group == group:
                group_size += 1
            else:
                result.append(last_group)
                sizes.append(group_size)
                last_group = group
                group_size = 1

        sizes.append(group_size)
        result.append(last_group)
        return result, sizes

