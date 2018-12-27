from summary.scope import session

PRIMARY_SLOTS_SCRUBBER_COUNTER = 8
PRIMARY_SLOTS_SCRUBBER = 24

SECONDARY_SLOTS_SCRUBBER_COUNTER = 56
SECONDARY_SLOTS_SCRUBBER = 72

BOOTLOADER_SCRUBBER_COUNTER = 104
BOOTLOADER_SCRUBBER = 120

SAFE_MODE_SCRUBBER_COUNTER = 152
SAFE_MODE_SCRUBBER = 168

BOOT_SETTINGS_SCRUBBER_COUNTER = 200

ITERATIONS_COUNT = 244


def dump_scrubbing_status(correlation_id):
    file_name = 'memory_content_{}'.format(correlation_id)
    out_file_name = 'scrubbing_{}.txt'.format(correlation_id)

    def dump_program(scrubber_offset, output):
        (offset, count, corrected) = unpack_binary_file(file_name, '<LLL',
                                                        from_byte=scrubber_offset + 16)
        (time_counter,) = unpack_binary_file(file_name, '<Q', from_byte=scrubber_offset - 16)

        output.write('\tOffset: {}\n'.format(offset))
        output.write('\tCount: {}\n'.format(count))
        output.write('\tCorrected: {}\n'.format(corrected))
        output.write('\tTime counter: {}ms\n'.format(time_counter))

    def dump_bootloader(output):
        (count, copies, mcu) = unpack_binary_file(file_name, '<LLL', from_byte=BOOTLOADER_SCRUBBER + 12)
        (time_counter,) = unpack_binary_file(file_name, '<Q', from_byte=BOOTLOADER_SCRUBBER_COUNTER)
        output.write('Bootloader scrubbing:\n')
        output.write('\tIterations count: {}\n'.format(count))
        output.write('\tCopies corrected: {}\n'.format(copies))
        output.write('\tMCU pages corrected: {}\n'.format(mcu))
        output.write('\tTime counter: {}ms\n'.format(time_counter))

    def dump_safe_mode(output):
        (count, copies, eeprom) = unpack_binary_file(file_name, '<LLL', from_byte=SAFE_MODE_SCRUBBER + 12)
        (time_counter,) = unpack_binary_file(file_name, '<Q', from_byte=SAFE_MODE_SCRUBBER_COUNTER)
        output.write('Safe mode scrubbing:\n')
        output.write('\tIterations count: {}\n'.format(count))
        output.write('\tCopies corrected: {}\n'.format(copies))
        output.write('\tEEPROM pages corrected: {}\n'.format(eeprom))
        output.write('\tTime counter: {}ms\n'.format(time_counter))

    def dump_boot_settings(output):
        (time_counter,) = unpack_binary_file(file_name, '<Q', from_byte=BOOT_SETTINGS_SCRUBBER_COUNTER)
        output.write('Boot settings scrubbing:\n')
        output.write('\tTime counter: {}ms\n'.format(time_counter))

    with session.open_artifact(out_file_name, 'w') as f:
        (iterations_count,) = unpack_binary_file(file_name, '<L', from_byte=ITERATIONS_COUNT)
        f.write('Iterations count: {}\n'.format(iterations_count))

        f.write('\n')
        f.write('Primary slots scrubbing:\n')
        dump_program(PRIMARY_SLOTS_SCRUBBER, f)

        f.write('\n')
        f.write('Secondary slots scrubbing:\n')
        dump_program(SECONDARY_SLOTS_SCRUBBER, f)

        f.write('\n')
        dump_bootloader(f)

        f.write('\n')
        dump_safe_mode(f)

        f.write('\n')
        dump_boot_settings(f)
